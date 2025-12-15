"""
Fragments for rendering programs.
"""

import json
from abc import ABC, abstractmethod
from urllib.parse import quote

from django.conf import settings
from django.contrib.sites.shortcuts import get_current_site
from django.http import Http404
from django.template.loader import render_to_string
from django.utils.translation import get_language
from django.utils.translation import gettext_lazy as _  # lint-amnesty, pylint: disable=unused-import
from django.utils.translation import to_locale
from lti_consumer.lti_1p1.contrib.django import lti_embed
from web_fragments.fragment import Fragment

from common.djangoapps.student.models import anonymous_id_for_user
from common.djangoapps.student.roles import GlobalStaff
from lms.djangoapps.learner_dashboard.utils import b2c_subscriptions_enabled, program_tab_view_is_enabled
from openedx.core.djangoapps.catalog.utils import get_programs
from openedx.core.djangoapps.plugin_api.views import EdxFragmentView
from openedx.core.djangoapps.programs.models import (
    ProgramDiscussionsConfiguration,
    ProgramLiveConfiguration,
    ProgramsApiConfig
)
from openedx.core.djangoapps.programs.utils import (
    ProgramProgressMeter,
    get_certificates,
    get_industry_and_credit_pathways,
    get_program_and_course_data,
    get_program_marketing_url,
    get_program_subscriptions_marketing_url,
    get_program_urls,
    get_programs_subscription_data
)
from openedx.core.djangoapps.user_api.preferences.api import get_user_preferences
from openedx.core.djangolib.markup import HTML
import requests
from openedx.core.djangoapps.user_api.accounts.utils import retrieve_last_sitewide_block_completed
from mx_course_discovery.models import LastReadCourse
from openedx.core.djangoapps.content.course_overviews.models import CourseOverview
from xmodule.modulestore.django import modulestore
from opaque_keys.edx.keys import CourseKey
import logging
logger = logging.getLogger(__name__)

class ProgramsFragmentView(EdxFragmentView):
    """
    A fragment to program listing.
    """

    def render_to_fragment(self, request, **kwargs):
        """
        Render the program listing fragment.
        """
        from lms.djangoapps.program_enrollments.models import ProgramEnrollment

        user = request.user
        try:
            mobile_only = json.loads(request.GET.get('mobile_only', 'false'))
        except ValueError:
            mobile_only = False

        programs_config = kwargs.get('programs_config') or ProgramsApiConfig.current()
        if not programs_config.enabled or not user.is_authenticated:
            raise Http404

        meter = ProgramProgressMeter(request.site, user, mobile_only=mobile_only)
        if meter.programs:
            user_enrolled_programs = ProgramEnrollment.objects.filter(user=user).values('program_uuid')
            user_enrolled_programs = [str(uuid['program_uuid']) for uuid in user_enrolled_programs]
            meter.programs = [program for program in meter.programs if program['uuid'] in user_enrolled_programs ]
            
            # url = settings.FEATURES['base_lms_url']+"explore-courses/enrolled-programs?username="+user.username+"&accept_language="+request.COOKIES.get("django_language", 'en')
            url = settings.FEATURES['base_lms_url']+"explore-courses/enrolled-programs?username="+user.username+"&accept_language="+request.COOKIES.get("lang", 'en')
            result = requests.get(url)
            if result.status_code == 200:
                if result.json():
                    for meter_program in meter.programs:
                        for result_program in result.json():
                            if meter_program['uuid'] == result_program['program_uuid']:
                                try:
                                    if (result_program['program_language'] == "") or (result_program['program_language'] == None):
                                        meter_program['program_language']="English"
                                    else:
                                        meter_program['program_language']=settings.LANGUAGE_DICT[result_program['program_language']]
                                except:
                                    meter_program['program_language']="English"
                                meter_program['title'] = result_program['converted_program_title']
                                for program_topics in result_program['tags']:
                                    if program_topics['tag_title'] not in meter_program['topics']:
                                        meter_program['topics'].append(program_topics['tag_title'])

        resume_block = dict()
        resume_block_url = retrieve_last_sitewide_block_completed(getattr(request.user, 'real_user', request.user))
        resume_block['resume_block_url'] = resume_block_url

        if resume_block_url:
            course_id = resume_block_url.split('/')[4]
            if course_id.startswith('course'):

                # Fetch program information
                programs = get_programs(course=course_id)
                prog_uuid = programs[0]['uuid'] if programs else None
                if prog_uuid:
                    # Check user enrollment
                    enrollment = ProgramEnrollment.objects.filter(
                        user=user,
                        program_uuid=prog_uuid
                    ).first()
                    
                    if enrollment:
                
                        resume_block['course_title'] = CourseOverview.objects.filter(id=course_id).first().display_name
                        resume_block['course_language'] = modulestore().get_course(CourseKey.from_string(course_id)).language
                        try:
                            resume_block['course_language_name'] = settings.LANGUAGE_DICT[modulestore().get_course(CourseKey.from_string(course_id)).language]
                        except:
                            resume_block['course_language_name'] = settings.LANGUAGE_DICT['en']
                        
                        user_last_read_course = LastReadCourse.objects.filter(user=user).first()
                        if user_last_read_course:
                            if user_last_read_course.last_read_program:
                                import ast            
                                resume_block['topics'] = ast.literal_eval(user_last_read_course.last_read_topics)
                                resume_block['program_title'] = user_last_read_course.last_read_program   

        is_user_b2c_subscriptions_enabled = b2c_subscriptions_enabled(mobile_only)
        programs_subscription_data = (
            get_programs_subscription_data(user)
            if is_user_b2c_subscriptions_enabled
            else []
        )
        subscription_upsell_data = (
            {
                'marketing_url': get_program_subscriptions_marketing_url(),
                'minimum_price': settings.SUBSCRIPTIONS_MINIMUM_PRICE,
                'trial_length': settings.SUBSCRIPTIONS_TRIAL_LENGTH,
            }
            if is_user_b2c_subscriptions_enabled
            else {}
        )
        
        context = {
            'marketing_url': get_program_marketing_url(programs_config, mobile_only),
            'programs': meter.engaged_programs,
            'progress': meter.progress(),
            'programs_subscription_data': programs_subscription_data,
            'subscription_upsell_data': subscription_upsell_data,
            'user_preferences': get_user_preferences(user),
            'is_user_b2c_subscriptions_enabled': is_user_b2c_subscriptions_enabled,
            'mobile_only': bool(mobile_only),
            'resume_block' : resume_block
        }
        html = render_to_string('learner_dashboard/programs_fragment.html', context)
        programs_fragment = Fragment(html)
        self.add_fragment_resource_urls(programs_fragment)

        return programs_fragment

    def standalone_page_title(self, request, fragment, **kwargs):
        """
        Return page title for the standalone page.
        """
        return _('Programs')


class ProgramDetailsFragmentView(EdxFragmentView):
    """
    Render the program details fragment.
    """

    @staticmethod
    def _get_resource_link_id(program_uuid, request) -> str:
        site = get_current_site(request)
        return f'{site.domain}-{program_uuid}'

    def render_to_fragment(self, request, program_uuid, **kwargs):  # lint-amnesty, pylint: disable=arguments-differ
        """View details about a specific program."""
        programs_config = kwargs.get('programs_config') or ProgramsApiConfig.current()
        user = request.user
        site = request.site
        if not programs_config.enabled or not request.user.is_authenticated:
            raise Http404
        try:
            mobile_only = json.loads(request.GET.get('mobile_only', 'false'))
        except ValueError:
            mobile_only = False

        program_data, course_data = get_program_and_course_data(site, user, program_uuid, mobile_only)

        if not program_data:
            raise Http404

        certificate_data = get_certificates(user, program_data)
        program_data.pop('courses')

        urls = get_program_urls(program_data)
        if not certificate_data:
            urls['program_record_url'] = None

        industry_pathways, credit_pathways = get_industry_and_credit_pathways(program_data, site)

        program_discussion_lti = ProgramDiscussionLTI(program_uuid, request)
        program_live_lti = ProgramLiveLTI(program_uuid, request)
        is_user_b2c_subscriptions_enabled = b2c_subscriptions_enabled(mobile_only)
        program_subscription_data = (
            get_programs_subscription_data(user, program_uuid)
            if is_user_b2c_subscriptions_enabled
            else []
        )

        def program_tab_view_enabled() -> bool:
            return program_tab_view_is_enabled() and (
                industry_pathways or
                credit_pathways or
                program_discussion_lti.is_configured or
                program_live_lti.is_configured
            )

        context = {
            'urls': urls,
            'user_preferences': get_user_preferences(user),
            'program_data': program_data,
            'program_subscription_data': program_subscription_data,
            'course_data': course_data,
            'certificate_data': certificate_data,
            'industry_pathways': industry_pathways,
            'credit_pathways': credit_pathways,
            'program_tab_view_enabled': program_tab_view_enabled(),
            'is_user_b2c_subscriptions_enabled': is_user_b2c_subscriptions_enabled,
            'subscriptions_trial_length': settings.SUBSCRIPTIONS_TRIAL_LENGTH,
            'discussion_fragment': {
                'configured': program_discussion_lti.is_configured,
                'iframe': program_discussion_lti.render_iframe()
            },
            'live_fragment': {
                'configured': program_live_lti.is_configured,
                'iframe': program_live_lti.render_iframe()
            }
        }
        html = render_to_string('learner_dashboard/program_details_fragment.html', context)
        program_details_fragment = Fragment(html)
        self.add_fragment_resource_urls(program_details_fragment)
        return program_details_fragment

    def standalone_page_title(self, request, fragment, **kwargs):
        """
        Return page title for the standalone page.
        """
        return _('Program Details')


class ProgramLTI(ABC):
    """
      Encapsulates methods for program LTI iframe rendering.
    """
    DEFAULT_ROLE = 'Student,Learner'
    ADMIN_ROLE = 'Administrator'

    def __init__(self, program_uuid, request):
        self.program_uuid = program_uuid
        self.program = get_programs(uuid=self.program_uuid)
        self.request = request
        self.configuration = self.get_configuration()

    @abstractmethod
    def get_configuration(self):
        return

    @property
    def is_configured(self):
        """
        Returns a boolean indicating if the program configuration is enabled or not.
        """
        return bool(self.configuration and self.configuration.enabled)

    def _get_resource_link_id(self) -> str:
        site = get_current_site(self.request)
        return f'{site.domain}-{self.program_uuid}'

    def _get_result_sourcedid(self, resource_link_id) -> str:
        return f'{self.program_uuid}:{resource_link_id}:{self.request.user.id}'

    def get_user_roles(self) -> str:
        """
        Returns comma-separated roles for the given user
        """
        basic_role = self.DEFAULT_ROLE

        if GlobalStaff().has_user(self.request.user):
            basic_role = self.ADMIN_ROLE

        all_roles = [basic_role]
        return ','.join(all_roles)

    def _get_additional_lti_parameters(self):
        lti_config = self.configuration.lti_configuration
        return lti_config.lti_config.get('additional_parameters', {})

    def _get_context_title(self) -> str:
        return "{} - {}".format(
            self.program.get('title', ''),
            self.program.get('subtitle', ''),
        )

    def _get_pii_lti_parameters(self, configuration, request):
        """
        Get LTI parameters that contain PII.

        Args:
            configuration (LtiConfiguration): LtiConfiguration object.
            request (HttpRequest): Request object for view in which LTI will be embedded.

        Returns:
            Dictionary with LTI parameters containing PII.
        """
        if configuration.version != configuration.LTI_1P1:
            return {}
        pii_config = {}
        if configuration.pii_share_username:
            pii_config['person_sourcedid'] = request.user.username
        if configuration.pii_share_email:
            pii_config['person_contact_email_primary'] = request.user.email
        return pii_config

    def _get_lti_embed_code(self) -> str:
        """
        Returns the LTI embed code for embedding in the program discussions tab
        Returns:
            HTML code to embed LTI in program page.
        """
        resource_link_id = self._get_resource_link_id()
        result_sourcedid = self._get_result_sourcedid(resource_link_id)
        pii_params = self._get_pii_lti_parameters(self.configuration.lti_configuration, self.request)
        additional_params = self._get_additional_lti_parameters()

        return lti_embed(
            html_element_id='lti-tab-launcher',
            lti_consumer=self.configuration.lti_configuration.get_lti_consumer(),
            resource_link_id=quote(resource_link_id),
            user_id=quote(anonymous_id_for_user(self.request.user, None)),
            roles=self.get_user_roles(),
            context_id=quote(self.program_uuid),
            context_title=self._get_context_title(),
            context_label=self.program_uuid,
            result_sourcedid=quote(result_sourcedid),
            locale=to_locale(get_language()),
            **pii_params,
            **additional_params
        )

    def render_iframe(self) -> str:
        """
        Returns the program LTI iframe if program Lti configuration exists for a program uuid
        """
        if not self.is_configured:
            return ''

        lti_embed_html = self._get_lti_embed_code()
        fragment = Fragment(
            HTML(
                """
                <iframe
                    id='lti-tab-embed'
                    style='width: 100%; min-height: 800px; border: none'
                    srcdoc='{srcdoc}'
                 >
                </iframe>
                """
            ).format(
                srcdoc=lti_embed_html
            )
        )
        return fragment.content


class ProgramDiscussionLTI(ProgramLTI):
    def get_configuration(self):
        return ProgramDiscussionsConfiguration.get(self.program_uuid)


class ProgramLiveLTI(ProgramLTI):
    def get_configuration(self):
        return ProgramLiveConfiguration.get(self.program_uuid)



# Manprax 

from django.core.serializers.json import DjangoJSONEncoder
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_GET
from lms.djangoapps.program_enrollments.models import ProgramEnrollment
import ast
@login_required
@require_GET
def program_listing_api(request):
    """
    API endpoint to return program listing data as JSON.
    URL - /dashboard/api/program-listing/
    """
    user = request.user
    mobile_only = False

    programs_config = ProgramsApiConfig.current()
    if not programs_config.enabled or not user.is_authenticated:
        return JsonResponse({'error': 'Not enabled or not authenticated'}, status=404)

    # Use ProgramProgressMeter directly
    meter = ProgramProgressMeter(request.site, user, mobile_only=mobile_only)
    if meter.programs:
        user_enrolled_programs = ProgramEnrollment.objects.filter(user=user).values('program_uuid')
        user_enrolled_programs = [str(uuid['program_uuid']) for uuid in user_enrolled_programs]
        meter.programs = [program for program in meter.programs if program['uuid'] in user_enrolled_programs]
        
        # lang = request.COOKIES.get("lang", 'en')
        # url = settings.FEATURES['base_lms_url'] + f"explore-courses/enrolled-programs?username={user.username}&accept_language={lang}"
        # result = requests.get(url)
        # if result.status_code == 200:
        #     if result.json():
        #         for meter_program in meter.programs:
        #             for result_program in result.json():
        #                 if meter_program['uuid'] == result_program['program_uuid']:
        #                     try:
        #                         if (result_program['program_language'] == "") or (result_program['program_language'] == None):
        #                             meter_program['program_language'] = "English"
        #                         else:
        #                             meter_program['program_language'] = settings.LANGUAGE_DICT[result_program['program_language']]
        #                     except:
        #                         meter_program['program_language'] = "English"
        #                     meter_program['title'] = result_program['converted_program_title']
        #                     for program_topics in result_program['tags']:
        #                         if program_topics['tag_title'] not in meter_program['topics']:
        #                             meter_program['topics'].append(program_topics['tag_title'])

    # Resume block logic
    resume_block = {}
    resume_block_url = retrieve_last_sitewide_block_completed(getattr(request.user, 'real_user', request.user))
    resume_block['resume_block_url'] = resume_block_url

    if resume_block_url:
        course_id = resume_block_url.split('/')[4]
        if course_id.startswith('course'):
            # Fetch program information
            programs = get_programs(course=course_id)
            prog_uuid = programs[0]['uuid'] if programs else None
            if prog_uuid:
                # Check user enrollment
                enrollment = ProgramEnrollment.objects.filter(
                    user=user,
                    program_uuid=prog_uuid
                ).first()
                
                if enrollment:
                    resume_block['course_title'] = CourseOverview.objects.filter(id=course_id).first().display_name
                    course_key = CourseKey.from_string(course_id)
                    course = modulestore().get_course(course_key)
                    resume_block['course_language'] = course.language
                    try:
                        resume_block['course_language_name'] = settings.LANGUAGE_DICT[course.language]
                    except:
                        resume_block['course_language_name'] = settings.LANGUAGE_DICT['en']
                    
                    user_last_read_course = LastReadCourse.objects.filter(user=user).first()
                    if user_last_read_course:
                        if user_last_read_course.last_read_program:
                            resume_block['topics'] = ast.literal_eval(user_last_read_course.last_read_topics)
                            resume_block['program_title'] = user_last_read_course.last_read_program   


    context = {
        'programs': meter.engaged_programs,
        'resume_block': resume_block
    }

    return JsonResponse(context, encoder=DjangoJSONEncoder)


























from openedx.core.djangoapps.site_configuration import helpers as configuration_helpers

from common.djangoapps.student.views.dashboard import (get_dashboard_course_limit, get_org_black_and_whitelist_for_site, get_course_enrollments, udateLastVisitedProgram,
get_filtered_course_entitlements, _create_recent_enrollment_message, complete_course_mode_info)

from common.djangoapps.course_modes.models import CourseMode
from lms.djangoapps.bulk_email.models import Optout
from lms.djangoapps.courseware.access import has_access
from common.djangoapps.student.helpers import cert_info, check_verify_status_by_course, get_resume_urls_for_enrollments
from django.db import transaction

# Manprax
@login_required
@require_GET
def student_program_course_api(request, program_uuid):
    """
    API endpoint to return student dashboard data as JSON for React.
    Simplified to essential data.
    """
    user = request.user

    # Essential config
    enable_verified_certificates = configuration_helpers.get_value(
        'ENABLE_VERIFIED_CERTIFICATES',
        settings.FEATURES.get('ENABLE_VERIFIED_CERTIFICATES')
    )
    display_course_modes_on_dashboard = configuration_helpers.get_value(
        'DISPLAY_COURSE_MODES_ON_DASHBOARD',
        settings.FEATURES.get('DISPLAY_COURSE_MODES_ON_DASHBOARD', True)
    )
    disable_course_limit = 'course_limit' in request.GET
    course_limit = get_dashboard_course_limit() if not disable_course_limit else None

    site_org_whitelist, site_org_blacklist = get_org_black_and_whitelist_for_site()
    course_enrollments = list(get_course_enrollments(user, site_org_whitelist, site_org_blacklist, course_limit))

    # Program title fetch
    program_title_url = settings.FEATURES['base_discovery_url'] + f"extandedapi/getprogram/?program_uuid={program_uuid}"
    program_title_response = requests.get(program_title_url)
    program_title = ''
    if program_title_response.status_code == 200 and program_title_response.json():
        program_title = program_title_response.json()[0]

    # Filter courses in program
    url = settings.FEATURES['base_discovery_url'] + f"extandedapi/getprogramcourses/?program_uuid={program_uuid}"
    response = requests.get(url)
    course_keys_in_program = []
    if response.status_code == 200:
        course_keys_in_program = response.json()
        course_enrollments = [enr for enr in course_enrollments if str(enr.course.id) in course_keys_in_program]

    # Update last visited program
    try:
        with transaction.atomic():  # Rolls back only this savepoint on error
            udateLastVisitedProgram(program_uuid, user)
    except Exception as err:
        logger.error(f"Error updating last visited program for UUID {program_uuid}: {str(err)}")

    # Entitlements (simplified)
    (course_entitlements,
     course_entitlement_available_sessions,
     unfulfilled_entitlement_pseudo_sessions) = get_filtered_course_entitlements(
        user, site_org_whitelist, site_org_blacklist
    )

    # Sort enrollments by start date
    course_enrollments.sort(key=lambda x: x.course.start, reverse=False)

    # Course modes (simplified)
    # enrolled_course_ids = [str(enr.course_id) for enr in course_enrollments]
    # __, unexpired_course_modes = CourseMode.all_and_unexpired_modes_for_courses(enrolled_course_ids)
    # # course_modes_by_course = {
    #     course_id: {mode.slug: mode for mode in modes}
    #     for course_id, modes in unexpired_course_modes.items()
    # }

    
    # Course languages
    course_languages = {}
    for course_key in course_keys_in_program:
        course = modulestore().get_course(CourseKey.from_string(course_key))
        if course:
            try:
                _ = settings.LANGUAGE_DICT[course.language]  # Just to check
                course_languages[course_key] = course.language
            except:
                course_languages[course_key] = "en"
        else:
            course_languages[course_key] = "en"

    # Resume URLs
    resume_button_urls = get_resume_urls_for_enrollments(user, course_enrollments)
    context = {
        'program_uuid': program_uuid,
        'program_title': program_title,
        'username': user.username,
        'course_enrollments': [serialize_enrollment(enr) for enr in course_enrollments],
        'course_entitlements': [serialize_entitlement(ent) for ent in course_entitlements],
        'course_entitlement_available_sessions': course_entitlement_available_sessions,
        'unfulfilled_entitlement_pseudo_sessions': unfulfilled_entitlement_pseudo_sessions,
        'course_languages': course_languages,
        'resume_button_urls': list(resume_button_urls.values()),
        'display_course_modes_on_dashboard': enable_verified_certificates and display_course_modes_on_dashboard,
        'nav_hidden': True,
        'show_program_listing': ProgramsApiConfig.is_enabled(),
        'show_dashboard_tabs': True,
        'disable_courseware_js': True,
    }
    return JsonResponse(context, encoder=DjangoJSONEncoder)


# Helper serializers
def serialize_enrollment(enrollment):
    course_overview = enrollment.course_overview
    return {
        'course_id': str(enrollment.course_id),
        'mode': enrollment.mode,
        'created': enrollment.created.isoformat() if enrollment.created else None,
        'course_overview': {
            'id': str(course_overview.id),
            'display_name_with_default': course_overview.display_name_with_default,
            'display_org_with_default': course_overview.display_org_with_default,
            'display_number_with_default': course_overview.display_number_with_default,
            'image_urls': getattr(course_overview, 'image_urls', {}),
            'has_ended': course_overview.has_ended(),
            'start_date_is_still_default': course_overview.start_date_is_still_default,
            'has_started': course_overview.has_started(),
            'starts_within': course_overview.starts_within(days=5),
            'dashboard_start_display': course_overview.dashboard_start_display.isoformat() if course_overview.dashboard_start_display else None,
            'end': course_overview.end.isoformat() if course_overview.end else None,
            'cert_name_long': course_overview.cert_name_long or settings.CERT_NAME_LONG,
            'language': getattr(course_overview, 'language', 'en'),
        },
        'is_paid': enrollment.is_paid_course(),
    }

def serialize_entitlement(entitlement):
    return {
        'uuid': str(entitlement.uuid),
        'course_uuid': str(entitlement.course_uuid),
        'mode': entitlement.mode,
        'expired_at_datetime': entitlement.expired_at_datetime.isoformat() if entitlement.expired_at_datetime else None,
        'enrollment_course_run': serialize_enrollment(entitlement.enrollment_course_run) if entitlement.enrollment_course_run else None,
        'days_until_expiration': entitlement.get_days_until_expiration(),
        'is_entitlement_refundable': entitlement.is_entitlement_refundable(),
    }