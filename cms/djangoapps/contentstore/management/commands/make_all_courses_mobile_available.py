"""
Django management command to migrate a course from the old Mongo modulestore
to the new split-Mongo modulestore.
"""


from django.contrib.auth.models import User
from django.core.management.base import BaseCommand, CommandError
from openedx.core.djangoapps.content.course_overviews.models import CourseOverview
import logging

class Command(BaseCommand):
    """
    Migrate a course from old-Mongo to split-Mongo. It reuses the old course id except where overridden.
    """

    

    def handle(self, *args, **options):
        all_courses_not_mobile_available = CourseOverview.objects.filter(mobile_available=False)

        for course in all_courses_not_mobile_available:

            try:
                logging.info("_________________course {} with course id {} is being mobile available true_________________".format(str(course.id),course.display_name))
                course.mobile_available = True
                course.save()
            except Exception as e:
                logging.info("_________________there is {} error in course {}_________________".format(e,str(course.id)))
                continue