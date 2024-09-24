"""
LibraryContent: The XBlock used to include blocks from a library in a course.
"""
from __future__ import annotations

import json
import logging
import random
from copy import copy
from gettext import ngettext, gettext

import bleach
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist, PermissionDenied
from django.utils.functional import classproperty
from lxml import etree
from lxml.etree import XMLSyntaxError
from opaque_keys import InvalidKeyError
from opaque_keys.edx.locator import LibraryLocator, LibraryLocatorV2
from rest_framework import status
from web_fragments.fragment import Fragment
from webob import Response
from xblock.completable import XBlockCompletionMode
from xblock.core import XBlock
from xblock.fields import Boolean, Integer, List, Scope, String

from xmodule.capa.responsetypes import registry
from xmodule.mako_block import MakoTemplateBlockBase
from xmodule.studio_editable import StudioEditableBlock
from xmodule.util.builtin_assets import add_webpack_js_to_fragment
from xmodule.validation import StudioValidation, StudioValidationMessage
from xmodule.xml_block import XmlMixin
from xmodule.x_module import (
    STUDENT_VIEW,
    ResourceTemplates,
    XModuleMixin,
    XModuleToXBlockMixin,
    shim_xmodule_js,
)
from xmodule.modulestore.django import modulestore
from xmodule.signals import RESULT_VIEWED

# Make '_' a no-op so we can scrape strings. Using lambda instead of
#  `django.utils.translation.ugettext_noop` because Django cannot be imported in this file
_ = lambda text: text

logger = logging.getLogger(__name__)

ANY_CAPA_TYPE_VALUE = 'any'


def _get_human_name(problem_class):
    """
    Get the human-friendly name for a problem type.
    """
    return getattr(problem_class, 'human_name', problem_class.__name__)


def _get_capa_types():
    """
    Gets capa types tags and labels
    """
    capa_types = {tag: _get_human_name(registry.get_class_for_tag(tag)) for tag in registry.registered_tags()}

    return [{'value': ANY_CAPA_TYPE_VALUE, 'display_name': _('Any Type')}] + sorted([
        {'value': capa_type, 'display_name': caption}
        for capa_type, caption in capa_types.items()
    ], key=lambda item: item.get('display_name'))


class LibraryToolsUnavailable(ValueError):
    """
    Raised when the library_tools service is requested in a runtime that doesn't provide it.
    """
    def __init__(self):
        super().__init__("Needed 'library_tools' features which were not available in the current runtime")


@XBlock.wants('library_tools')  # TODO: Split this service into its LMS and CMS parts.
@XBlock.wants('studio_user_permissions')  # Only available in CMS.
@XBlock.wants('user')
@XBlock.needs('mako')
class LibraryContentBlock(
    MakoTemplateBlockBase,
    XmlMixin,
    XModuleToXBlockMixin,
    ResourceTemplates,
    XModuleMixin,
    StudioEditableBlock,
):
    """
    An XBlock whose children are chosen dynamically from a content library.
    Can be used to create randomized assessments among other things.

    Note: technically, all matching blocks from the content library are added
    as children of this block, but only a subset of those children are shown to
    any particular student.
    """
    # pylint: disable=abstract-method
    has_children = True
    has_author_view = True

    resources_dir = 'assets/library_content'

    mako_template = 'widgets/metadata-edit.html'
    studio_js_module_name = "VerticalDescriptor"

    show_in_read_only_mode = True

    # noinspection PyMethodParameters
    @classproperty
    def completion_mode(cls):  # pylint: disable=no-self-argument
        """
        Allow overriding the completion mode with a feature flag.

        This is a property, so it can be dynamically overridden in tests, as it is not evaluated at runtime.
        """
        if settings.FEATURES.get('MARK_LIBRARY_CONTENT_BLOCK_COMPLETE_ON_VIEW', False):
            return XBlockCompletionMode.COMPLETABLE

        return XBlockCompletionMode.AGGREGATOR

    display_name = String(
        display_name=_("Display Name"),
        help=_("The display name for this component."),
        default="Randomized Content Block",
        scope=Scope.settings,
    )
    source_library_id = String(
        display_name=_("Library"),
        help=_("Select the library from which you want to draw content."),
        scope=Scope.settings,
        values_provider=lambda instance: instance.source_library_values(),
    )
    source_library_version = String(
        # This is a hidden field that stores the version of source_library when we last pulled content from it
        display_name=_("Library Version"),
        scope=Scope.settings,
    )
    mode = String(
        display_name=_("Mode"),
        help=_("Determines how content is drawn from the library"),
        default="random",
        # Manprax
        values=[
            {"display_name": _("Random"), "value": "random"},
            {"display_name": _("Ratio"), "value": "ratio"}
            # Future addition: Choose a new random set of n every time the student refreshes the block, for self tests
            # Future addition: manually selected blocks
        ],
        scope=Scope.settings,
    )
    # mode_test = String(
    #     display_name=_("Mode tet"),
    #     help=_("Determines how content is drawn from the library"),
    #     default="random",
    #     # Manprax
    #     values=[
    #         {"display_name": _("Random"), "value": "random"},
    #         {"display_name": _("Ratio"), "value": "ratio"}
    #         # Future addition: Choose a new random set of n every time the student refreshes the block, for self tests
    #         # Future addition: manually selected blocks
    #     ],
    #     scope=Scope.settings,
    # )
    max_count = Integer(
        display_name=_("Count"),
        help=_("Enter the number of components to display to each student. Set it to -1 to display all components."),
        default=1,
        scope=Scope.settings,
    )
    capa_type = String(
        display_name=_("Problem Type"),
        help=_('Choose a problem type to fetch from the library. If "Any Type" is selected no filtering is applied.'),
        default=ANY_CAPA_TYPE_VALUE,
        values=_get_capa_types(),
        scope=Scope.settings,
    )
    selected = List(
        # This is a list of (block_type, block_id) tuples used to record
        # which random/first set of matching blocks was selected per user
        default=[],
        scope=Scope.user_state,
    )

    already_selected = List(
        # This is a list of (block_type, block_id) tuples used to record
        # which random/first set of matching blocks was selected per user
        default=[],
        scope=Scope.user_state,
    )
    # This cannot be called `show_reset_button`, because children blocks inherit this as a default value.
    allow_resetting_children = Boolean(
        display_name=_("Show Reset Button"),
        help=_("Determines whether a 'Reset Problems' button is shown, so users may reset their answers and reshuffle "
               "selected items."),
        scope=Scope.settings,
        default=False
    )

    # Manprax 

    ratio = String(
        display_name=_("Ratio"),
        help=_("Enter the ratio e.g. Hard:Medium:Low if ration is not provided then the default ration would be 1:4:5"),
        default="1:4:5",
        scope=Scope.settings,
    )
    attempts = Integer(
        help=_("Number of attempts taken by the student"),
        default=0,
        scope=Scope.user_state
    )
    attempt_allowed = Integer(
        display_name=_("Maximum Attempts Allowed"),
        help=_("Defines the number of times a student can try to answer this problem."),
        values={"min": 1}, scope=Scope.settings
    )
    search_prompt = String(
        display_name=_("Search Prompt"),
        help=_("Enter the Search Prompt to search about this course e.g. 'photosynthesis' "),
        default="",
        scope=Scope.settings,
    )
    chatgpt_prompt = String(
        display_name=_("ChatGpt Prompt"),
        help=_("Enter the ChatGpt Prompt to search about this course e.g. 'photosynthesis in plants' "),
        default="",
        scope=Scope.settings,
    )
    result_summary = String(
        display_name=_("result summary of html block"),
        help=_("Enter the html content of the result summary"),
        default="<h1>Result<h1>",
        scope=Scope.settings,
    )
    course_connected=String(
        display_name=_("course connected"),
        help=_("Enter the course_id of the course to be connected to this quiz"),
        default="",
        scope=Scope.settings,
    )
   
    @property
    def source_library_key(self):
        """
        Convenience method to get the library ID as a LibraryLocator and not just a string.

        Supports either library v1 or library v2 locators.
        """
        try:
            return LibraryLocator.from_string(self.source_library_id)
        except InvalidKeyError:
            return LibraryLocatorV2.from_string(self.source_library_id)

    @classmethod
    def make_selection(cls, selected, children, max_count, attempts, attempt_allowed, ratio, mode,already_selected,block_parent_id,course_id):
        """
        Dynamically selects block_ids indicating which of the possible children are displayed to the current user.

        Arguments:
            selected - list of (block_type, block_id) tuples assigned to this student
            children - children of this block
            max_count - number of components to display to each student
            mode - how content is drawn from the library

        Returns:
            A dict containing the following keys:

            'selected' (set) of (block_type, block_id) tuples assigned to this student
            'invalid' (set) of dropped (block_type, block_id) tuples that are no longer valid
            'overlimit' (set) of dropped (block_type, block_id) tuples that were previously selected
            'added' (set) of newly added (block_type, block_id) tuples
        """
        rand = random.Random()

        selected_keys = {tuple(k) for k in selected}  # set of (block_type, block_id) tuples assigned to this student

        # Determine which of our children we will show:
        valid_block_keys = {(c.block_type, c.block_id) for c in children}

        # Remove any selected blocks that are no longer valid:
        invalid_block_keys = (selected_keys - valid_block_keys)
        if invalid_block_keys:
            selected_keys -= invalid_block_keys

        current_ratio = "1:4:5"
        try:
            if attempts <= attempt_allowed:
                split_ratio = ratio.split(",")
                current_ratio = split_ratio[attempts]
        except Exception as err:
            logger.error("{}".format(err))
        # If max_count has been decreased, we may have to drop some previously selected blocks:
        overlimit_block_keys = set()
        if len(selected_keys) > max_count and mode == "random":
            num_to_remove = len(selected_keys) - max_count
            overlimit_block_keys = set(rand.sample(list(selected_keys), num_to_remove))
            selected_keys -= overlimit_block_keys
        
        # Manprax 
        # If max_count has been decreased, we may have to drop some previously selected blocks and mode is ratio
        if len(selected_keys) > max_count and current_ratio and mode == "ratio":
            mx_valid_block_keys = get_block_based_ratio(current_ratio, max_count, children,already_selected,block_parent_id,course_id)
            added_block_keys = mx_valid_block_keys
            selected_keys = added_block_keys

        # Do we have enough blocks now?
        num_to_add = max_count - len(selected_keys)

        added_block_keys = None
        if num_to_add > 0:
            # We need to select [more] blocks to display to this user:
            pool = valid_block_keys - selected_keys
            if mode == "random":
                num_to_add = min(len(pool), num_to_add)
                added_block_keys = set(rand.sample(list(pool), num_to_add))
                # We now have the correct n random children to show for this user.

            # Manprax 
            # If mode is ratio and need to show extra block to User.
            elif current_ratio and mode == "ratio":
                mx_valid_block_keys = get_block_based_ratio(current_ratio, max_count, children,already_selected,block_parent_id,course_id)
                added_block_keys = mx_valid_block_keys
                selected_keys = added_block_keys

            else:
                raise NotImplementedError("Unsupported mode.")
            selected_keys |= added_block_keys

        if any((invalid_block_keys, overlimit_block_keys, added_block_keys)):
            selected = list(selected_keys)
            random.shuffle(selected)

        return {
            'selected': selected,
            'invalid': invalid_block_keys,
            'overlimit': overlimit_block_keys,
            'added': added_block_keys,
        }

    def _publish_event(self, event_name, result, **kwargs):
        """
        Helper method to publish an event for analytics purposes
        """
        event_data = {
            "location": str(self.location),
            "result": result,
            "previous_count": getattr(self, "_last_event_result_count", len(self.selected)),
            "max_count": self.max_count,
        }
        event_data.update(kwargs)
        self.runtime.publish(self, f"edx.librarycontentblock.content.{event_name}", event_data)
        self._last_event_result_count = len(result)  # pylint: disable=attribute-defined-outside-init

    @classmethod
    def publish_selected_children_events(cls, block_keys, format_block_keys, publish_event):
        """
        Helper method for publishing events when children blocks are
        selected/updated for a user.  This helper is also used by
        the ContentLibraryTransformer.

        Arguments:

            block_keys -
                A dict describing which events to publish (add or
                remove), see `make_selection` above for format details.

            format_block_keys -
                A function to convert block keys to the format expected
                by publish_event. Must have the signature:

                    [(block_type, block_id)] -> T

                Where T is a collection of block keys as accepted by
                `publish_event`.

            publish_event -
                Function that handles the actual publishing.  Must have
                the signature:

                    <'removed'|'assigned'> -> result:T -> removed:T -> reason:str -> None

                Where T is a collection of block_keys as returned by
                `format_block_keys`.
        """
        if block_keys['invalid']:
            # reason "invalid" means deleted from library or a different library is now being used.
            publish_event(
                "removed",
                result=format_block_keys(block_keys['selected']),
                removed=format_block_keys(block_keys['invalid']),
                reason="invalid"
            )

        if block_keys['overlimit']:
            publish_event(
                "removed",
                result=format_block_keys(block_keys['selected']),
                removed=format_block_keys(block_keys['overlimit']),
                reason="overlimit"
            )

        if block_keys['added']:
            publish_event(
                "assigned",
                result=format_block_keys(block_keys['selected']),
                added=format_block_keys(block_keys['added'])
            )

    def selected_children(self):
        """
        Returns a [] of block_ids indicating which of the possible children
        have been selected to display to the current user.

        This reads and updates the "selected" field, which has user_state scope.

        Note: the return value (self.selected) contains block_ids. To get
        actual BlockUsageLocators, it is necessary to use self.children,
        because the block_ids alone do not specify the block type.
        """
        max_count = self.max_count
        if max_count < 0:
            max_count = len(self.children)


        # from lms.djangoapps.courseware.models import StudentModule

        # block_keys = self.make_selection(self.selected, self.children, max_count, "random")  # pylint: disable=no-member
        # Manprax
        block_keys = self.make_selection(self.selected, self.children, max_count, self.attempts, self.attempt_allowed, self.ratio, self.mode,self.already_selected,self.parent,self.course_id)  # pylint: disable=no-member

        # Publish events for analytics purposes:
        lib_tools = self.get_tools()
        format_block_keys = lambda keys: lib_tools.create_block_analytics_summary(self.location.course_key, keys)
        self.publish_selected_children_events(
            block_keys,
            format_block_keys,
            self._publish_event,
        )

        if any(block_keys[changed] for changed in ('invalid', 'overlimit', 'added')):
            # Save our selections to the user state, to ensure consistency:
            selected = block_keys['selected']
            self.selected = selected  # TODO: this doesn't save from the LMS "Progress" page.
        for select in self.selected:
            self.already_selected.append(select[1])

        return self.selected

    @XBlock.handler
    def reset_selected_children(self, _, __):
        """
        Resets the XBlock's state for a user.

        This resets the state of all `selected` children and then clears the `selected` field
        so that the new blocks are randomly chosen for this user.
        """
        # if not self.allow_resetting_children:
        #     return Response('"Resetting selected children" is not allowed for this XBlock',
        #                     status=status.HTTP_400_BAD_REQUEST)
        #resetting the grade to reset the selected answers for the blocks
        
        self.runtime.publish(self, 'grade', {'value': None, 'max_value': None})
        for block_type, block_id in self.selected_children():
            block = self.runtime.get_block(self.location.course_key.make_usage_key(block_type, block_id))
            logger.info("__________________________________ block.get_score :{} \n \n \n\n\n ".format(block.get_score))
            logger.info("__________________________________ __________________________________________________________________")
            if hasattr(block, 'reset_problem'):
                block.reset_problem(None)
                block.save()
        self.attempts += 1
        self.selected = []
        # Manprax
        # self.attempts += 1
        return Response(json.dumps(self.student_view({}).content))
    
    # Manprax
    @XBlock.handler
    def check_attempts(self, _, __):
        """
        Show Attempts made by a user.
        """
        if self.attempts < self.attempt_allowed:
            attempt_allowed = {'attempt_allowed': True}
        else:
            attempt_allowed = {'attempt_allowed': False}

        
        return Response(json.dumps(attempt_allowed))

    @XBlock.handler
    def show_user_result(self, _, __):
        """
        Show results to User.
        """
        from lms.djangoapps.grades.api import CourseGradeFactory
        from django.contrib.auth.models import User
        from mx_catalog.models import Content
        from mx_catalog.views import get_course
        from mx_catalog.serializers import ContentDetailSerializer
        show_reset = True
        is_passed = False
        has_attempt = True
        user_id = self.get_user_id()
        correct_count=0
        total_possible=0
        user = User.objects.get(id = user_id)
        user_grade = CourseGradeFactory().read(user, course_key = self.location.course_key)
        if user_grade.passed:
            is_passed = True
        test_val=[]
        course_content_data=[]
        
        for block_key, block_structure in user_grade.chapter_grades.items():
            for a in dict(block_structure['sections'][0].problem_scores).keys():
                if block_structure['sections'][0].problem_scores[a].earned == block_structure['sections'][0].problem_scores[a].possible:
                    correct_count=correct_count+1
                total_possible= total_possible+1
        
        if self.course_connected:
            try:
                course_content_mapped =  Content.objects.get(source_id = self.course_connected)
                serializer = ContentDetailSerializer(course_content_mapped)
                course_content_data = serializer.data
            except:
                course_content_data=[]
        course_data = get_course(self.course_id,user)
        param = {
            "show_reset": show_reset,
            "is_passed": is_passed,
            "attempt_number":self.attempts,
            "has_attempt": has_attempt,
            "search_prompt":self.search_prompt,
            "chatgpt_prompt":self.chatgpt_prompt,
            "total_correct":correct_count,
            "total_possible":total_possible,
            "course_content_data":course_content_data,
            "result_summary":self.result_summary,
            "course_data":course_data
        }
        RESULT_VIEWED.send(sender=CourseGradeFactory,
                        instance=user_grade,
                        user_id=user_id,
                        content_key=self.location.course_key,
                        target=total_possible
                        )
        return Response(json.dumps(param))

    def _get_selected_child_blocks(self):
        """
        Generator returning XBlock instances of the children selected for the
        current user.
        """
        for block_type, block_id in self.selected_children():
            yield self.runtime.get_block(self.location.course_key.make_usage_key(block_type, block_id))

    def student_view(self, context):  # lint-amnesty, pylint: disable=missing-function-docstring
        fragment = Fragment()
        contents = []
        child_context = {} if not context else copy(context)

        for child in self._get_selected_child_blocks():
            if child is None:
                # TODO: Fix the underlying issue in TNL-7424
                # This shouldn't be happening, but does for an as-of-now
                # unknown reason. Until we address the underlying issue,
                # let's at least log the error explicitly, ignore the
                # exception, and prevent the page from resulting in a
                # 500-response.
                logger.error('Skipping display for child block that is None')
                continue

            rendered_child = child.render(STUDENT_VIEW, child_context)
            fragment.add_fragment_resources(rendered_child)
            contents.append({
                'id': str(child.location),
                'content': rendered_child.content,
            })

        fragment.add_content(self.runtime.service(self, 'mako').render_lms_template('vert_module.html', {
            'items': contents,
            'xblock_context': context,
            'show_bookmark_button': False,
            'watched_completable_blocks': set(),
            'completion_delay_ms': None,
            'reset_button': self.allow_resetting_children,
        }))

        fragment.add_javascript_url(self.runtime.local_resource_url(self, 'public/js/library_content_reset.js'))
        fragment.initialize_js('LibraryContentReset')
        return fragment

    def author_view(self, context):
        """
        Renders the Studio views.
        Normal studio view: If block is properly configured, displays library status summary
        Studio container view: displays a preview of all possible children.
        """
        fragment = Fragment()
        root_xblock = context.get('root_xblock')
        is_root = root_xblock and root_xblock.location == self.location
        try:
            is_updating = self.get_tools().are_children_syncing(self)
        except LibraryToolsUnavailable:
            is_updating = False
        if is_root and not is_updating:
            # User has clicked the "View" link. Show a preview of all possible children:
            if self.children:  # pylint: disable=no-member
                max_count = self.max_count
                if max_count < 0:
                    max_count = len(self.children)

                fragment.add_content(self.runtime.service(self, 'mako').render_cms_template(
                    "library-block-author-preview-header.html", {
                        'max_count': max_count,
                        'display_name': self.display_name or self.url_name,
                    }))
                context['can_edit_visibility'] = False
                context['can_move'] = False
                context['can_collapse'] = True
                self.render_children(context, fragment, can_reorder=False, can_add=False)
        # else: When shown on a unit page, don't show any sort of preview -
        # just the status of this block in the validation area.
        context['is_loading'] = is_updating

        # The following JS is used to make the "Update now" button work on the unit page and the container view:
        if root_xblock and 'library' in root_xblock.category:
            if root_xblock.source_library_id and len(root_xblock.children) > 0:
                fragment.add_javascript_url(self.runtime.local_resource_url(self, 'public/js/library_content_edit.js'))
        else:
            fragment.add_javascript_url(self.runtime.local_resource_url(self, 'public/js/library_content_edit.js'))

        fragment.initialize_js('LibraryContentAuthorView')
        return fragment

    def studio_view(self, _context):
        """
        Return the studio view.
        """
        fragment = Fragment(
            self.runtime.service(self, 'mako').render_cms_template(self.mako_template, self.get_context())
        )
        fragment.add_javascript_url(self.runtime.local_resource_url(self, 'public/js/library_content_edit_helpers.js'))
        add_webpack_js_to_fragment(fragment, 'LibraryContentBlockEditor')
        shim_xmodule_js(fragment, self.studio_js_module_name)
        return fragment

    def get_child_blocks(self):
        """
        Return only the subset of our children relevant to the current student.
        """
        return list(self._get_selected_child_blocks())

    @property
    def non_editable_metadata_fields(self):
        non_editable_fields = super().non_editable_metadata_fields
        # The only supported mode is currently 'random'.
        # Add the mode field to non_editable_metadata_fields so that it doesn't
        # render in the edit form.
        non_editable_fields.extend([
            # LibraryContentBlock.mode,
            LibraryContentBlock.source_library_version,
        ])
        return non_editable_fields

    def get_tools(self, to_read_library_content: bool = False) -> 'LibraryToolsService':
        """
        Grab the library tools service and confirm that it'll work for us. Else, raise LibraryToolsUnavailable.
        """
        if tools := self.runtime.service(self, 'library_tools'):
            if (not to_read_library_content) or tools.can_use_library_content(self):
                return tools
        raise LibraryToolsUnavailable()

    def get_user_id(self):
        """
        Get the ID of the current user.
        """
        user_service = self.runtime.service(self, 'user')
        if user_service:
            user_id = user_service.get_current_user().opt_attrs.get('edx-platform.user_id', None)
        else:
            user_id = None
        return user_id

    def _validate_sync_permissions(self):
        """
        Raises PermissionDenied() if we can't confirm that user has write on this block and read on source library.

        If source library isn't set, then that's OK.
        """
        if not (user_perms := self.runtime.service(self, 'studio_user_permissions')):
            raise PermissionDenied("Access cannot be validated in the current runtime.")
        if not user_perms.can_write(self.scope_ids.usage_id.context_key):
            raise PermissionDenied(f"Cannot write to block at {self.scope_ids.usage_id}")
        if self.source_library_key:
            if not user_perms.can_read(self.source_library_key):
                raise PermissionDenied(f"Cannot read library at {self.source_library_key}")

    @XBlock.handler
    def upgrade_and_sync(self, request=None, suffix=None):  # pylint: disable=unused-argument
        """
        HTTP handler allowing Studio users to update to latest version of source library and synchronize children.

        This is a thin wrapper around `sync_from_library(upgrade_to_latest=True)`, plus permission checks.

        Returns 400 if libraray tools or user permission services are not available.
        Returns 403/404 if user lacks read access on source library or write access on this block.
        """
        self._validate_sync_permissions()
        if not self.source_library_id:
            return Response(_("Source content library has not been specified."), status=400)
        try:
            self.sync_from_library(upgrade_to_latest=True)
        except LibraryToolsUnavailable:
            return Response(_("Content libraries are not available in the current runtime."), status=400)
        except ObjectDoesNotExist:
            return Response(
                _("Source content library does not exist: {source_library_id}").format(
                    source_library_id=self.source_library_id
                ),
                status=400,
            )
        return Response()

    def sync_from_library(self, upgrade_to_latest: bool = False) -> None:
        """
        Synchronize children with source library.

        If `upgrade_to_latest==True` or if source library version is unset, update library version to latest.
        Otherwise, use current source library version.

        Raises ObjectDoesNotExist if library or version is missing.
        """
        self.get_tools(to_read_library_content=True).trigger_library_sync(
            dest_block=self,
            library_version=(None if upgrade_to_latest else self.source_library_version),
        )

    @XBlock.json_handler
    def is_v2_library(self, data, suffix=''):  # pylint: disable=unused-argument
        """
        Check the library version by library_id.

        This is a temporary handler needed for hiding the Problem Type xblock editor field for V2 libraries.
        """
        lib_key = data.get('library_key')
        try:
            LibraryLocatorV2.from_string(lib_key)
        except InvalidKeyError:
            is_v2 = False
        else:
            is_v2 = True
        return {'is_v2': is_v2}

    @XBlock.handler
    def children_are_syncing(self, request, suffix=''):  # pylint: disable=unused-argument
        """
        Returns whether this block is currently having its children updated from the source library.
        """
        try:
            is_updating = self.get_tools().are_children_syncing(self)
        except LibraryToolsUnavailable:
            is_updating = False
        return Response(json.dumps(is_updating))

    def studio_post_duplicate(self, store, source_block):
        """
        Used by the studio after basic duplication of a source block. We handle the children
        ourselves, because we have to properly reference the library upstream and set the overrides.

        Otherwise we'll end up losing data on the next refresh.
        """
        if hasattr(super(), 'studio_post_duplicate'):
            super().studio_post_duplicate(store, source_block)

        self._validate_sync_permissions()
        self.get_tools(to_read_library_content=True).trigger_duplication(source_block=source_block, dest_block=self)
        return True  # Children have been handled.

    def studio_post_paste(self, store, source_node) -> bool:
        """
        Pull the children from the library and let library_tools assign their IDs.
        """
        if hasattr(super(), 'studio_post_paste'):
            super().studio_post_paste(store, source_node)

        self.sync_from_library(upgrade_to_latest=False)
        return True  # Children have been handled

    def _validate_library_version(self, validation, lib_tools, version, library_key):
        """
        Validates library version
        """
        latest_version = lib_tools.get_latest_library_version(library_key)
        if latest_version is not None:
            if version is None or version != latest_version:
                validation.set_summary(
                    StudioValidationMessage(
                        StudioValidationMessage.WARNING,
                        _('This component is out of date. The library has new content.'),
                        # TODO: change this to action_runtime_event='...' once the unit page supports that feature.
                        # See https://openedx.atlassian.net/browse/TNL-993
                        action_class='library-update-btn',
                        # Translators: {refresh_icon} placeholder is substituted to "↻" (without double quotes)
                        action_label=_("{refresh_icon} Update now.").format(refresh_icon="↻")
                    )
                )
                return False
        else:
            validation.set_summary(
                StudioValidationMessage(
                    StudioValidationMessage.ERROR,
                    _('Library is invalid, corrupt, or has been deleted.'),
                    action_class='edit-button',
                    action_label=_("Edit Library List.")
                )
            )
            return False
        return True

    def _set_validation_error_if_empty(self, validation, summary):
        """  Helper method to only set validation summary if it's empty """
        if validation.empty:
            validation.set_summary(summary)

    def validate(self):
        """
        Validates the state of this Library Content Block Instance. This
        is the override of the general XBlock method, and it will also ask
        its superclass to validate.
        """
        validation = super().validate()
        if not isinstance(validation, StudioValidation):
            validation = StudioValidation.copy(validation)
        try:
            lib_tools = self.get_tools(to_read_library_content=True)
        except LibraryToolsUnavailable:
            validation.set_summary(
                StudioValidationMessage(
                    StudioValidationMessage.ERROR,
                    _(
                        "This course does not support content libraries. "
                        "Contact your system administrator for more information."
                    )
                )
            )
            return validation
        if not self.source_library_id:
            validation.set_summary(
                StudioValidationMessage(
                    StudioValidationMessage.NOT_CONFIGURED,
                    _("A library has not yet been selected."),
                    action_class='edit-button',
                    action_label=_("Select a Library.")
                )
            )
            return validation
        self._validate_library_version(validation, lib_tools, self.source_library_version, self.source_library_key)

        # Note: we assume children have been synced
        # since the last time fields like source_library_id or capa_types were changed.
        matching_children_count = len(self.children)  # pylint: disable=no-member
        if matching_children_count == 0:
            self._set_validation_error_if_empty(
                validation,
                StudioValidationMessage(
                    StudioValidationMessage.WARNING,
                    (gettext('There are no problems in the specified library of type {capa_type}.'))
                    .format(capa_type=self.capa_type),
                    action_class='edit-button',
                    action_label=_("Select another problem type.")
                )
            )

        if matching_children_count < self.max_count:
            self._set_validation_error_if_empty(
                validation,
                StudioValidationMessage(
                    StudioValidationMessage.WARNING,
                    (
                        ngettext(
                            'The specified library is configured to fetch {count} problem, ',
                            'The specified library is configured to fetch {count} problems, ',
                            self.max_count
                        ) +
                        ngettext(
                            'but there is only {actual} matching problem.',
                            'but there are only {actual} matching problems.',
                            matching_children_count
                        )
                    ).format(count=self.max_count, actual=matching_children_count),
                    action_class='edit-button',
                    action_label=_("Edit the library configuration.")
                )
            )

        return validation

    def source_library_values(self):
        """
        Return a list of possible values for self.source_library_id
        """
        lib_tools = self.get_tools()
        user_perms = self.runtime.service(self, 'studio_user_permissions')
        all_libraries = [
            (key, bleach.clean(name)) for key, name in lib_tools.list_available_libraries()
            if user_perms.can_read(key) or self.source_library_id == str(key)
        ]
        all_libraries.sort(key=lambda entry: entry[1])  # Sort by name
        if self.source_library_id and self.source_library_key not in [entry[0] for entry in all_libraries]:
            all_libraries.append((self.source_library_id, _("Invalid Library")))
        all_libraries = [("", _("No Library Selected"))] + all_libraries
        values = [{"display_name": name, "value": str(key)} for key, name in all_libraries]
        return values

    def post_editor_saved(self, user, old_metadata, old_content):  # pylint: disable=unused-argument
        """
        If source library or capa_type have been edited, upgrade library & sync automatically.

        TODO: capa_type doesn't really need to trigger an upgrade once we've migrated to V2.
        """
        source_lib_changed = (self.source_library_id != old_metadata.get("source_library_id", ""))
        capa_filter_changed = (self.capa_type != old_metadata.get("capa_type", ANY_CAPA_TYPE_VALUE))
        if source_lib_changed or capa_filter_changed:
            try:
                self.sync_from_library(upgrade_to_latest=True)
            except (ObjectDoesNotExist, LibraryToolsUnavailable):
                # The validation area will display an error message, no need to do anything now.
                pass

    def has_dynamic_children(self):
        """
        Inform the runtime that our children vary per-user.
        See get_child_blocks() above
        """
        return True

    def get_content_titles(self):
        """
        Returns list of friendly titles for our selected children only; without
        thi, all possible children's titles would be seen in the sequence bar in
        the LMS.

        This overwrites the get_content_titles method included in x_module by default.
        """
        titles = []
        for child in self.get_child_blocks():
            titles.extend(child.get_content_titles())
        return titles

    @classmethod
    def definition_from_xml(cls, xml_object, system):
        children = []

        for child in xml_object.getchildren():
            try:
                children.append(system.process_xml(etree.tostring(child)).scope_ids.usage_id)
            except (XMLSyntaxError, AttributeError):
                msg = (
                    "Unable to load child when parsing Library Content Block. "
                    "This can happen when a comment is manually added to the course export."
                )
                logger.error(msg)
                if system.error_tracker is not None:
                    system.error_tracker(msg)

        definition = dict(xml_object.attrib.items())
        return definition, children

    def definition_to_xml(self, resource_fs):
        """ Exports Library Content Block to XML """
        xml_object = etree.Element('library_content')
        for child in self.get_children():
            self.runtime.add_block_as_child_node(child, xml_object)
        # Set node attributes based on our fields.
        for field_name, field in self.fields.items():  # pylint: disable=no-member
            if field_name in ('children', 'parent', 'content'):
                continue
            if field.is_set_on(self):
                xml_object.set(field_name, str(field.read_from(self)))
        return xml_object


class LibrarySummary:
    """
    A library summary object which contains the fields required for library listing on studio.
    """

    def __init__(self, library_locator, display_name):
        """
        Initialize LibrarySummary

        Arguments:
        library_locator (LibraryLocator):  LibraryLocator object of the library.

        display_name (unicode): display name of the library.
        """
        self.display_name = display_name if display_name else _("Empty")

        self.id = library_locator  # pylint: disable=invalid-name
        self.location = library_locator.make_usage_key('library', 'library')

    @property
    def display_org_with_default(self):
        """
        Org display names are not implemented. This just provides API compatibility with CourseBlock.
        Always returns the raw 'org' field from the key.
        """
        return self.location.library_key.org

    @property
    def display_number_with_default(self):
        """
        Display numbers are not implemented. This just provides API compatibility with CourseBlock.
        Always returns the raw 'library' field from the key.
        """
        return self.location.library_key.library
    

# Manprax
def get_block_based_ratio(ratio, max_count, children,already_selected,block_parent_id,course_id):
    from openedx_tagging.core.tagging.models import ObjectTag
    from xmodule.modulestore.django import modulestore
    get_ratio = ratio.split(":")
    hard = medium = low = ""
    complexity_hard = 'Hard'
    complexity_medium = 'Medium'
    complexity_low = 'Low'
    total_hard = total_medium = total_low = 0

    # Get hard, medium, low value for ratio 
    try:
        hard = int(get_ratio[0])
        medium = int(get_ratio[1])
        low = int(get_ratio[2])
    except Exception as err:
        logger.error("{}".format(err))
        pass

    # calculate total number of hard, medium, low from given ratio.
    try:
        total_hard = int((hard*max_count*10)/100) if hard else ""
        total_medium = int((medium*max_count*10)/100) if medium else ""
        total_low = int((low*max_count*10)/100) if low else ""
    except Exception as err:
        logger.error("{}".format(err))
        pass
    count_hard = count_medium = count_low = remaining_count =0

    mx_valid_block_keys = set()
    course_competency = []
    # For hard xblock
    all_tag_objects = ObjectTag.objects.all()

    # Fetch particular quiz competency if does not exist check competency of the course
    try:
        quiz_competency = all_tag_objects.get(object_id =str(block_parent_id),taxonomy__name='Competencies')
    except:
        quiz_competency= []
    # if quiz_competency(competency of the unit block) does not exist check competency of the course
    if not quiz_competency:
        try:
            quiz_competency = all_tag_objects.get(object_id =str(course_id),taxonomy__name='Competencies')
        except:
            quiz_competency=[]
    all_probelm_blocks_list=[]
    
    ''''
    Added By Manprax
    Fetch all the blocks in the question bank(library) with quiz selected competency
    
    This adds the list of the problem all_probelm_blocks_list :
    {
        block_type : Type of block eg. problem, library etc.
        block_id : block_id of the content present in the course(Not the block_id defined in the library ).
        competency_name : Competency name of the block(problem)
        Complexity_name : Complexity of the block i.e Hard, Medium, Low.
    }

    '''
    for get_children in children:
        problem_library = modulestore().get_block_original_usage(get_children)
        problem_library_id= str(problem_library[0])
        try:
            competency_name = all_tag_objects.get(object_id=problem_library_id , taxonomy__name='Competencies')._value
        except:
            competency_name=''
        try:
            complexity_name = all_tag_objects.get(object_id=problem_library_id , taxonomy__name='Complexities')._value
        except:
            #considering a problem low if no complexity is defined
            complexity_name='low'
        if quiz_competency and competency_name == quiz_competency._value:
            problem_block_dict ={
                'block_type':get_children.block_type,
                'block_id':get_children.block_id,
                'competency_name':competency_name,
                'complexity_name':complexity_name,
            }
            all_probelm_blocks_list.append(problem_block_dict)
    ''' End of adding '''
    # competency_problem_clock = [comptency for comptency in all_probelm_blocks_list if comptency['competency_name'] == quiz_competency]
    random.shuffle(all_probelm_blocks_list)
    # select hard problems first
    def select_problem_blocks(count_problem,complexity,total_count):
        for select_problem in all_probelm_blocks_list:
            if count_problem < total_count and select_problem['complexity_name'] == complexity and select_problem['block_id'] not in already_selected:
                count_problem=+1
                block = (select_problem['block_type'],select_problem['block_id'])
                mx_valid_block_keys.add(tuple(block))
        return count_problem
    
    def already_select_problems(count_problem,complexity,total_count):
        for select_problem in all_probelm_blocks_list:
            if complexity:
                if count_problem < total_count and select_problem['complexity_name'] == complexity:
                    count_problem=+1
                    block = (select_problem['block_type'],select_problem['block_id'])
                    mx_valid_block_keys.add(tuple(block))
            else:
                if count_problem < total_count:
                    count_problem=+1
                    block = (select_problem['block_type'],select_problem['block_id'])
                    mx_valid_block_keys.add(tuple(block))
        return count_problem
    
    if len(set(already_selected)) < len(all_probelm_blocks_list):
        count_hard = select_problem_blocks(count_hard,complexity_hard,total_hard)
        remaining_hard = total_hard - count_hard
        total_medium += remaining_hard
        count_medium = select_problem_blocks(count_medium,complexity_medium,total_medium)
        remaining_medium = total_medium - count_medium
        total_low += remaining_medium
        count_low = select_problem_blocks(count_low,complexity_low,total_low)
        if total_low - count_low > 0:
            already_select_problems(remaining_count,'',total_low-count_low)

    else:
        count_hard = already_select_problems(count_hard,complexity_hard,total_hard)
        remaining_hard = total_hard - count_hard
        total_medium += remaining_hard
        count_medium = already_select_problems(count_medium,complexity_medium,total_medium)
        remaining_medium = total_medium - count_medium
        total_low += remaining_medium
        count_low = already_select_problems(count_low,complexity_low,total_low)
        if total_low - count_low > 0:
            already_select_problems(remaining_count,'',total_low)


    return mx_valid_block_keys
