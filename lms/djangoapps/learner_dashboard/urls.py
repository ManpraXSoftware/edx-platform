"""Learner dashboard URL routing configuration"""

from django.urls import path, re_path

from lms.djangoapps.learner_dashboard import programs, program_views
from lms.djangoapps.learner_dashboard.programs import program_listing_api, student_program_course_api


urlpatterns = [
    path('', program_views.program_listing, name='program_listing_view'),
    path('programs/', program_views.program_listing, name='program_listing_view'),
    path('mxprograms/', program_views.mx_program_listing, name='mxprogram_listing_view'),
    re_path(r'^programs/(?P<program_uuid>[0-9a-f-]+)/$', program_views.program_details, name='program_details_view'),
    re_path(r'^programs/(?P<program_uuid>[0-9a-f-]+)/discussion/$', program_views.ProgramDiscussionIframeView.as_view(),
            name='program_discussion'),
    re_path(r'^programs/(?P<program_uuid>[0-9a-f-]+)/live/$', program_views.ProgramLiveIframeView.as_view(),
            name='program_live'),
    path('programs_fragment/', programs.ProgramsFragmentView.as_view(), name='program_listing_fragment_view'),
    re_path(r'^programs/(?P<program_uuid>[0-9a-f-]+)/details_fragment/$', programs.ProgramDetailsFragmentView.as_view(),
            name='program_details_fragment_view'),

    # Manprax
    path('api/program-listing/', program_listing_api, name='program_listing_api'),
    re_path(r'^api/student-program-course-api/(?P<program_uuid>[0-9a-f-]+)/$', student_program_course_api, name='student_program_course_api'),

]
