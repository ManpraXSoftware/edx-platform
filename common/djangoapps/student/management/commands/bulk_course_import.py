import os
import openpyxl
from django.core.management.base import BaseCommand
from xmodule.modulestore.django import modulestore
from xmodule.modulestore import ModuleStoreEnum
from opaque_keys.edx.locator import CourseLocator
# from xmodule.course_module import DEFAULT_START_DATE
from cms.djangoapps.contentstore.xblock_storage_handlers.create_xblock import create_xblock
from datetime import datetime
from django.contrib.auth import get_user_model
from django.conf import settings
from mx_catalog.models import Content,Content_List,Tag,ContentTag_Mapper,Content_Category,SubscriptionCatalog
import logging
from django.test.client import RequestFactory
from cms.djangoapps.contentstore.xblock_storage_handlers.view_handlers import modify_xblock
import json
log = logging.getLogger(__name__)
import requests
from io import BytesIO
import re

DEFAULT_START_DATE = datetime(2025, 1, 1)  # Adjust as needed

from django.core.files.base import File

class Command(BaseCommand):
    help = "Create course from Excel"
    @staticmethod
    def download_youtube_thumbnail(video_id):
        thumbnail_url = f"https://img.youtube.com/vi/{video_id}/maxresdefault.jpg"
        response = requests.get(thumbnail_url)
        if response.status_code == 200 and response.content:
            return BytesIO(response.content)
        return None

    def handle(self, *args, **options):
          # Debugging breakpoint
        excel_file = os.path.dirname(__file__)+'/static/bulk_import_6_7.xlsx'  # Make sure it's in your working dir or use full path
        workbook = openpyxl.load_workbook(excel_file)
        sheet = workbook.active

        store = modulestore()
        User = get_user_model()
        user = User.objects.get(username=settings.DEFAULT_USER_NAME)  # must be a course staff

        for row in sheet.iter_rows(min_row=2, values_only=True):
            grade = row[0]
            subject = row[2]
            course_name= row[5]
            video_url = row[7]
            org = "AA"
            number = re.sub(r'\s+', '_', re.sub(r'[^\w\s]', '', course_name)).lower()
            # number = course_name.replace(",", "").replace("?", "").replace("-", "").replace('(','').replace(')','').replace('&','').replace(':','').replace('"', '').replace("'", "").replace(" ", "_").lower()
            run = "2025-2026"
            course_key = CourseLocator(org=org, course=number, run=run)
            # Create course
            if store.get_course(course_key):
                log.info("Course : %s already Exist :",course_key)
                continue

            log.info(f"🛠 Creating course {course_key}")
            logging.info(f"Creating course {course_key} with org={org}, number={number}, run={run}")
            course = store.create_course(
                org=org,
                course=number,
                run=run,
                user_id=user.id,
                fields={
                    'display_name': course_name,
                    'start': DEFAULT_START_DATE,
                    "mobile_available": True
                }
            )
            logging.info(f"Course {course_key} created successfully.")
            section = create_xblock(str(course.location),user , 'chapter', display_name="Section")
            subsection = create_xblock(str(section.location),user, 'sequential', display_name="Subsection")
            unit = create_xblock(str(subsection.location),user,  'vertical', display_name="Video")
            youtube_id = video_url.split("/")[-1]
            logging.info(f"Creating video XBlock with YouTube ID: {youtube_id}")
            metadata = {
                'display_name': 'Video',
                'youtube_id_1_0': youtube_id,
                'edx_video_id': '',
                'html5_sources': [],
                'track': '',
                'license': '',
                'start_time': "00:00:00",
                'end_time': "00:00:00"
            }
            video_block = create_xblock(
                str(unit.location),
                user,
                'video',
                display_name=' Video',
                
            )
            request_data = {
                'category': 'video',
                'courseKey': str(course_key),
                'display_name': ' Video',
                'id': str(video_block.location.block_id),
                'metadata': {
                    'display_name': ' Video',
                    'edx_video_id': '',
                    'html5_sources': [],
                    'youtube_id_1_0': youtube_id,
                    'track': '',
                    'start_time': '00:00:00',
                    'end_time': '00:00:00',
                    'license': ''
                }
            }
            factory = RequestFactory()
            request = factory.post(
                path='/xblock/block-create/',  # can be anything
                data=json.dumps(request_data),
                content_type='application/json'
            )
            request.user = user

            request.json = request_data
            modify_xblock(video_block.location,request)
            store.publish(course.location, user.id)
            thumbnail_io = self.download_youtube_thumbnail(youtube_id)
            
            logging.info(f"Course structure created for {course_key} with section, subsection, and unit.")
            content = Content.objects.get(source_identity=str(course_key))

            if thumbnail_io:
                thumbnail_io.name = f"{youtube_id}.jpg"
                django_file = File(thumbnail_io, name=thumbnail_io.name)
                content.icon = django_file

            tags_list = [grade, subject,'English']
            tags = Tag.objects.translated(language_code='en').filter(translations__value__in=tags_list)
            try:
                content_list= Content_List.objects.translated(language_code='en').get(translations__name=subject,category__translations__name=grade)
                logging.info(f"Content list {content_list} found for subject {subject} and grade {grade}.")
            except Content_List.DoesNotExist:
                logging.info(f"Content list not found for subject {subject} and grade {grade}, creating new one.")
                content_category= Content_Category.objects.translated(language_code='en').filter(translations__name=grade).first()
                content_list = Content_List.objects.create(
                    list_name=str(subject),
                    category_id=content_category.id if content_category else None,
                    order=1,
                    internal_name=subject.replace(" ", "_").lower()+'_en_'+grade.replace(" ", "_").lower(),
                    format_type = 'normal',
                    subscription = SubscriptionCatalog.objects.get(subscription_name='FREE') ,
                    created_by=user,
                    modified_by=user,
                    mode='normal',
                )
                content_list.set_current_language('en')
                content_list.name = subject
                content_list.save()
                logging.info(f"Content list {content_list} created for subject {subject} and grade {grade}.")
            if content:
                # for con_list in content_list:
                content.lists.add(content_list)
                content.list_id_text = " ".join(["list_{}".format(content_list.id)])
                logging.info(f"Content {content} added to content list {content_list}.")
                # for tag in tags:
                content.tag_label = ' '.join(tag.value for tag in tags)
                for tag in tags:
                    ContentTag_Mapper.objects.get_or_create(
                        content=content,
                        tag=tag
                    )
                    logging.info(f"Tag {tag} added to content {content}.")
                content.save()
           
