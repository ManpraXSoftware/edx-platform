"""
Fragments for rendering programs.
"""


import json

from django.http import Http404
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils.translation import get_language_bidi, ugettext_lazy as _
from web_fragments.fragment import Fragment
from django.conf import settings

from lms.djangoapps.commerce.utils import EcommerceService
from lms.djangoapps.learner_dashboard.utils import FAKE_COURSE_KEY, strip_course_id
from openedx.core.djangoapps.catalog.constants import PathwayType
from openedx.core.djangoapps.catalog.utils import get_pathways
from openedx.core.djangoapps.credentials.utils import get_credentials_records_url
from openedx.core.djangoapps.plugin_api.views import EdxFragmentView
from openedx.core.djangoapps.programs.models import ProgramsApiConfig
from openedx.core.djangoapps.programs.utils import (
    ProgramDataExtender,
    ProgramProgressMeter,
    get_certificates,
    get_program_marketing_url
)
from openedx.core.djangoapps.user_api.preferences.api import get_user_preferences
from openedx.core.djangoapps.content.course_overviews.models import CourseOverview
import requests

class ProgramsFragmentView(EdxFragmentView):
    """
    A fragment to program listing.
    """
    def render_to_fragment(self, request, **kwargs):
        """
        Render the program listing fragment.
        """
        user = request.user
        try:
            mobile_only = json.loads(request.GET.get('mobile_only', 'false'))
        except ValueError:
            mobile_only = False

        programs_config = kwargs.get('programs_config') or ProgramsApiConfig.current()
        if not programs_config.enabled or not user.is_authenticated:
            raise Http404

        meter = ProgramProgressMeter(request.site, user, mobile_only=mobile_only)
        # import pdb;pdb.set_trace()

        
        if meter.programs:
            from lms.djangoapps.program_enrollments.models import ProgramEnrollment
            user_enrolled_programs = ProgramEnrollment.objects.filter(user=user).values('program_uuid')
            user_enrolled_programs = [str(uuid['program_uuid']) for uuid in user_enrolled_programs]
            
            meter.programs = [program for program in meter.programs if program['uuid'] in user_enrolled_programs ]
            
            url = settings.FEATURES['base_lms_url']+"explore-courses/enrolled-programs?username="+user.username+"&accept_language=en"
            result = requests.get(url)
            
            if result.status_code == 200:
                if result.json():
                    for meter_program in meter.programs:
                        for result_program in result.json():
                            if meter_program['uuid'] == result_program['program_uuid']:
                                for program_topics in result_program['tags']:
                                    meter_program['topics'].append(program_topics['tag_title'])


        resume_block = dict()
        from openedx.core.djangoapps.user_api.accounts.utils import retrieve_last_sitewide_block_completed
        resume_block_url = retrieve_last_sitewide_block_completed(getattr(request.user, 'real_user', request.user))

        resume_block['resume_block_url'] = resume_block_url

        if resume_block_url:
            course_id = resume_block_url.split('/')[4]
            
            # import pdb;pdb.set_trace()
            if course_id.startswith('course'):
                resume_block['course_title'] = CourseOverview.objects.filter(id=course_id).first().display_name
                from openedx.core.djangoapps.programs.models import LastReadCourse
                # from lms.djangoapps.program_enrollments.models import ProgramEnrollment
                user_last_read_course = LastReadCourse.objects.filter(user=user).first()
                # import pdb;pdb.set_trace()
                if user_last_read_course:
                    if user_last_read_course.last_read_program:
                        import ast            
                        resume_block['topics'] = ast.literal_eval(user_last_read_course.last_read_topics)
                        resume_block['program_title'] = user_last_read_course.last_read_program
                    # resume_block['course_title'] = CourseOverview.objects.filter(id=course_id).first().display_name
                # url = "https://staging-courses.visionempowertrust.org/"+"extandedapi/getprogramusingcourseid/?course_id="+course_id
                # url = settings.FEATURES['base_discovery_url']+"extandedapi/getprogramusingcourseid/?course_id="+course_id
                
                # response = requests.get(url)

                # if response.status_code == 200:
                #     program_detail = response.json()
                #     if program_detail:
                        
                #         resume_block['topics'] = program_detail['topics']
                #         resume_block['program_title'] = program_detail['program_title']
                #         resume_block['course_title'] = CourseOverview.objects.filter(id=course_id).first().display_name
                    

                # import pdb;pdb.set_trace()
                
                

        # import pdb;pdb.set_trace()
        context = {
            'marketing_url': get_program_marketing_url(programs_config, mobile_only),
            # 'marketing_url': 'https://staging-lms.visionempowertrust.org',
            'programs': meter.engaged_programs,
            'progress': meter.progress(),
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

    def css_dependencies(self):
        """
        Returns list of CSS files that this view depends on.

        The helper function that it uses to obtain the list of CSS files
        works in conjunction with the Django pipeline to ensure that in development mode
        the files are loaded individually, but in production just the single bundle is loaded.
        """
        if get_language_bidi():
            return self.get_css_dependencies('style-learner-dashboard-rtl')
        else:
            return self.get_css_dependencies('style-learner-dashboard')


class ProgramDetailsFragmentView(EdxFragmentView):
    """
    Render the program details fragment.
    """
    def render_to_fragment(self, request, program_uuid, **kwargs):
        """View details about a specific program."""
        
        
        programs_config = kwargs.get('programs_config') or ProgramsApiConfig.current()
        if not programs_config.enabled or not request.user.is_authenticated:
            raise Http404

        meter = ProgramProgressMeter(request.site, request.user, uuid=program_uuid)
        program_data = meter.programs[0]
        if not program_data:
            raise Http404

        try:
            mobile_only = json.loads(request.GET.get('mobile_only', 'false'))
        except ValueError:
            mobile_only = False

        program_data = ProgramDataExtender(program_data, request.user, mobile_only=mobile_only).extend()
        course_data = meter.progress(programs=[program_data], count_only=False)[0]
        certificate_data = get_certificates(request.user, program_data)

        program_data.pop('courses')
        skus = program_data.get('skus')
        ecommerce_service = EcommerceService()

        # TODO: Don't have business logic of course-certificate==record-available here in LMS.
        # Eventually, the UI should ask Credentials if there is a record available and get a URL from it.
        # But this is here for now so that we can gate this URL behind both this business logic and
        # a waffle flag. This feature is in active developoment.
        program_record_url = get_credentials_records_url(program_uuid=program_uuid)
        if not certificate_data:
            program_record_url = None

        industry_pathways = []
        credit_pathways = []
        try:
            for pathway_id in program_data['pathway_ids']:
                pathway = get_pathways(request.site, pathway_id)
                if pathway and pathway['email']:
                    if pathway['pathway_type'] == PathwayType.CREDIT.value:
                        credit_pathways.append(pathway)
                    elif pathway['pathway_type'] == PathwayType.INDUSTRY.value:
                        industry_pathways.append(pathway)
        # if pathway caching did not complete fully (no pathway_ids)
        except KeyError:
            pass

        urls = {
            'program_listing_url': reverse('program_listing_view'),
            'track_selection_url': strip_course_id(
                reverse('course_modes_choose', kwargs={'course_id': FAKE_COURSE_KEY})
            ),
            'commerce_api_url': reverse('commerce_api:v0:baskets:create'),
            'buy_button_url': ecommerce_service.get_checkout_page_url(*skus),
            'program_record_url': program_record_url,
        }

        context = {
            'urls': urls,
            'user_preferences': get_user_preferences(request.user),
            'program_data': program_data,
            'course_data': course_data,
            'certificate_data': certificate_data,
            'industry_pathways': industry_pathways,
            'credit_pathways': credit_pathways,
        }

        # import pdb;pdb.set_trace()
        html = render_to_string('learner_dashboard/program_details_fragment.html', context)
        program_details_fragment = Fragment(html)
        self.add_fragment_resource_urls(program_details_fragment)
        return program_details_fragment

    def standalone_page_title(self, request, fragment, **kwargs):
        """
        Return page title for the standalone page.
        """
        return _('Program Details')

    def css_dependencies(self):
        """
        Returns list of CSS files that this view depends on.

        The helper function that it uses to obtain the list of CSS files
        works in conjunction with the Django pipeline to ensure that in development mode
        the files are loaded individually, but in production just the single bundle is loaded.
        """
        if get_language_bidi():
            return self.get_css_dependencies('style-learner-dashboard-rtl')
        else:
            return self.get_css_dependencies('style-learner-dashboard')
