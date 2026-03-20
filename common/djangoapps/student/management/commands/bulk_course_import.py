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
from django.utils.timezone import now


DEFAULT_START_DATE = datetime(2025, 1, 1)  # Adjust as needed

from django.core.files.base import File

from urllib.parse import urlparse, parse_qs





def extract_youtube_id(url: str) -> str | None:
    """
    Extract YouTube video ID from all common YouTube URL formats.
    Returns None if ID cannot be determined.
    """
    if not url:
        return None

    url = url.strip()

    # 1. Raw ID (sometimes clients send just the ID)
    if re.fullmatch(r"[A-Za-z0-9_-]{11}", url):
        return url

    parsed = urlparse(url)

    # 2. youtu.be/<id>
    if parsed.netloc in {"youtu.be", "www.youtu.be"}:
        return parsed.path.lstrip("/") or None

    # 3. youtube.com/watch?v=<id>
    if parsed.netloc in {
        "youtube.com",
        "www.youtube.com",
        "m.youtube.com",
        "music.youtube.com",
    }:
        query = parse_qs(parsed.query)
        if "v" in query:
            return query["v"][0]

    # 4. youtube.com/embed/<id>
    if parsed.path.startswith("/embed/"):
        return parsed.path.split("/embed/")[-1]

    # 5. youtube.com/shorts/<id>
    if parsed.path.startswith("/shorts/"):
        return parsed.path.split("/shorts/")[-1]

    # 6. Fallback regex (last resort)
    match = re.search(
        r"(?:v=|\/)([A-Za-z0-9_-]{11})(?:\?|&|\/|$)",
        url,
    )
    if match:
        return match.group(1)

    return None

class Command(BaseCommand):
    help = "Create course from Excel"
    @staticmethod
    def download_youtube_thumbnail(video_id):
        thumbnail_url = f"https://img.youtube.com/vi/{video_id}/maxresdefault.jpg"
        response = requests.get(thumbnail_url)
        if response.status_code == 200 and response.content:
            return BytesIO(response.content)
        return None

    def _create_course_in_lms(self, store, user, org, number, run, course_name, course_key, youtube_id):
        """Create course, structure, and video block in LMS."""
        logging.info(f"Creating course {course_key} with org={org}, number={number}, run={run}")
        course = store.create_course(
            org=org,
            course=number,
            run=run,
            user_id=user.id,
            fields={
                "display_name": course_name,
                "start": DEFAULT_START_DATE,
                "enrollment_start": now(),
                "enrollment_end": None,
                "mobile_available": True,
                "self_paced": True,
                "visible_to_staff_only": False,
            }
        )
        logging.info(f"Course {course_key} created successfully.")
        section = create_xblock(str(course.location), user, 'chapter', display_name="Section")
        subsection = create_xblock(str(section.location), user, 'sequential', display_name="Subsection")
        unit = create_xblock(str(subsection.location), user, 'vertical', display_name="Video")
        logging.info(f"Creating video XBlock with YouTube ID: {youtube_id}")
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
            path='/xblock/block-create/',
            data=json.dumps(request_data),
            content_type='application/json'
        )
        request.user = user
        request.json = request_data
        modify_xblock(video_block.location, request)
        store.publish(course.location, user.id)
        logging.info(f"Course structure created for {course_key} with section, subsection, and unit.")

    def _add_content_mapping(self, user, course_key, youtube_id, grade, subject, medium):
        """Add content mapping (Content_List, Tags) for mobile app visibility."""
        thumbnail_io = self.download_youtube_thumbnail(youtube_id)
        content = Content.objects.get(source_identity=str(course_key))
        if thumbnail_io:
            thumbnail_io.name = f"{youtube_id}.jpg"
            django_file = File(thumbnail_io, name=thumbnail_io.name)
            content.icon = django_file

        tags_list = [grade, subject, medium]
        tags = Tag.objects.translated(language_code='en').filter(translations__value__in=tags_list)
        content_list = Content_List.objects.translated(language_code='en').filter(
            translations__name=subject,
            category__translations__name=medium
        ).first()

        if content_list:
            logging.info(f"Content list {content_list} found for subject {subject} and grade {grade}.")
        else:
            logging.info(f"Content list not found for subject {subject} and grade {grade}, creating new one.")

            content_category = Content_Category.objects.translated(language_code='en').filter(
                translations__name=medium
            ).first()

            content_list = Content_List.objects.create(
                list_name=str(subject),
                category_id=content_category.id if content_category else None,
                order=1,
                internal_name=f"{subject.replace(' ', '_').lower()}_en_{grade.replace(' ', '_').lower()}",
                format_type='normal',
                subscription=SubscriptionCatalog.objects.get(subscription_name='FREE'),
                created_by=user,
                modified_by=user,
                mode='normal',
            )

            content_list.set_current_language('en')
            content_list.name = subject
            content_list.save()

            logging.info(f"Content list {content_list} created for subject {subject} and grade {grade}.")

        if content:
            content.lists.add(content_list)
            content.list_id_text = " ".join(["list_{}".format(content_list.id)])
            logging.info(f"Content {content} added to content list {content_list}.")
            content.tag_label = ' '.join(tag.value for tag in tags)
            for tag in tags:
                ContentTag_Mapper.objects.get_or_create(
                    content=content,
                    tag=tag
                )
                logging.info(f"Tag {tag} added to content {content}.")
            content.save()

    def handle(self, *args, **options):

        imported_count = 0
        video_url_skipped_count = 0
        course_repeat_skipped_count = 0
        error_count = 0
        mapping_only_count = 0

        excel_file = os.path.dirname(__file__)+'/static/Mapping Grade 1-10 Multiple Languages -Month March 2026.xlsx'
        workbook = openpyxl.load_workbook(excel_file)
        sheet = workbook.active

        store = modulestore()
        User = get_user_model()
        user = User.objects.get(username="devops_team")

        for row in sheet.iter_rows(min_row=2, values_only=True):

            grade = f"grade {str(row[1]).strip()}"

            subject = (row[2] or "").strip()
            medium = (row[3] or "").strip()
            lesson = (row[4] or "").strip()

            if not subject or not medium:
                logging.error(f"Skipping row due to missing subject/medium: {row}")
                continue
            course_name = f"{lesson}-{medium}" if medium else lesson
            video_url = (row[5] or "").strip()
            org = "AA"
            number = re.sub(r'\s+', '_', re.sub(r'[^\w\s]', '', course_name)).lower()
            logging.info(f"Processing row: {row}")
            run = "2025-2026"
            course_key = CourseLocator(org=org, course=number, run=run)

            # Validate video URL
            if not video_url:
                video_url_skipped_count += 1
                logging.error(f"Video URL is missing for course {course_name}. Skipping this row.")
                continue

            # Extract YouTube ID early (needed for both course creation and thumbnail)
            youtube_id = extract_youtube_id(video_url)
            if not youtube_id:
                error_count += 1
                logging.error(f"Invalid YouTube URL: {video_url}")
                continue

            # --- Determine current state ---
            course_in_lms = store.get_course(course_key) is not None
            content_obj = Content.objects.filter(source_identity=str(course_key)).first()
            has_mapping = False
            medium_resolved = medium if medium else 'English'
            if content_obj:
                _cl = Content_List.objects.translated(language_code='en').filter(
                    translations__name=subject,
                    category__translations__name=medium_resolved
                ).first()
                if _cl and content_obj.lists.filter(id=_cl.id).exists():
                    has_mapping = True

            # Case 1: Both course and mapping already exist → skip entirely
            if course_in_lms and has_mapping:
                course_repeat_skipped_count += 1
                log.info("Course %s already exists with mapping. Skipping.", course_key)
                continue

            # Case 2: Course not in LMS → create course + structure + video
            if not course_in_lms:
                log.info(f"🛠 Creating course {course_key}")
                self._create_course_in_lms(store, user, org, number, run, course_name, course_key, youtube_id)
            else:
                # Course exists in LMS but mapping is missing
                mapping_only_count += 1
                log.info("Course %s exists in LMS but missing mapping. Adding mapping only.", course_key)

            # Add mapping if missing (for both new courses and existing ones without mapping)
            if not has_mapping:
                self._add_content_mapping(user, course_key, youtube_id, grade, subject, medium_resolved)

            imported_count += 1

        self.stdout.write(self.style.SUCCESS(
            f"\nImport completed\n"
            f"Imported courses      : {imported_count}\n"
            f"Mapping only added    : {mapping_only_count}\n"
            f"Skipped (both exist)  : {course_repeat_skipped_count}\n"
            f"Skipped (no video)    : {video_url_skipped_count}\n"
            f"Errors                : {error_count}\n"
        ))
