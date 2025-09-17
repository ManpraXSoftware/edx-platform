from xmodule.modulestore.django import modulestore
from opaque_keys.edx.keys import CourseKey

from xmodule.modulestore.django import modulestore
from opaque_keys.edx.keys import CourseKey
from mx_catalog.models import Tag,ContentTag_Mapper,Content
from django.contrib.auth import get_user_model
from django.conf import settings
from cms.djangoapps.contentstore.xblock_storage_handlers.view_handlers import modify_xblock
from django.test.client import RequestFactory
import json
import requests
from io import BytesIO
import re
from django.core.files.base import File
from django.core.management.base import BaseCommand


def download_youtube_thumbnail(video_id):
    thumbnail_url = f"https://img.youtube.com/vi/{video_id}/maxresdefault.jpg"
    response = requests.get(thumbnail_url)
    if response.status_code == 200 and response.content:
        return BytesIO(response.content)
    return None

class Command(BaseCommand): 
    """
    This script is used to create csv for basic reports like, Total active users, Quiz attempt rate and course engagement rate.
    """
    def add_arguments(self, parser):
            parser.add_argument('medium', type=str, help='Update data from particular language ')
    def handle(self, *args, **options):
        language = str(options['medium'])
        class_tags = Tag.objects.get(content_filter__translations__name="Medium",translations__value=language)
        content_ids = ContentTag_Mapper.objects.filter(tag=class_tags).values_list("content_id", flat=True)
        content_keys = Content.objects.filter(id__in=content_ids).values_list("source_identity", flat=True)
        for content_id in content_keys:
            course_key = CourseKey.from_string(str(content_id))
            store = modulestore()
            course = store.get_course(course_key)
            User = get_user_model()
            user = User.objects.get(username=settings.DEFAULT_USER_NAME)
            section_locations = course.children  # these are BlockUsageLocator objects
            video_block=''
            section = store.get_item(section_locations[0])
            subsection = store.get_item(section.children[0])
            unit = store.get_item(subsection.children[0])
            block = store.get_item(unit.children[0])
            if block.location.block_type == 'video':
                video_block = block.location
            
            youtube_id= block.youtube_id_1_0.replace('?','')
            request_data = {
                        'category': 'video',
                        'courseKey': str(content_id),
                        'display_name': 'Video',
                        'id': str(video_block.block_id),
                        'metadata': {
                            'display_name': 'Video',
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
                path='/xblock/block-create/', 
                data=json.dumps(request_data),
                content_type='application/json'
                )
            request.user = user

            request.json = request_data

            modify_xblock(video_block,request)
            store.publish(course.location, user.id)
            thumbnail_io = download_youtube_thumbnail(youtube_id)
            content = Content.objects.get(source_identity=str(content_id))
            if thumbnail_io:
                thumbnail_io.name = f"{youtube_id}.jpg"
                django_file = File(thumbnail_io, name=thumbnail_io.name)
                content.icon = django_file
                content.save()


