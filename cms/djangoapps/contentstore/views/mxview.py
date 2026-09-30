"""
Token-authenticated wrappers around existing CMS handlers.

SessionAuthentication is intentionally excluded: DRF enforces CSRF inside
SessionAuthentication.authenticate() and @csrf_exempt cannot intercept it.
Removing it means CSRF is never checked, which is correct for a token-only API.
"""
import json

from opaque_keys import InvalidKeyError
from opaque_keys.edx.keys import CourseKey
from rest_framework import status
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from edx_rest_framework_extensions.auth.jwt.authentication import JwtAuthentication
from openedx.core.djangoapps.content.course_overviews.models import CourseOverview
from openedx.core.lib.api.authentication import (
    BearerAuthenticationAllowInactiveUser,
    OAuth2AuthenticationAllowInactiveUser,
)

from cms.djangoapps.contentstore.xblock_storage_handlers.view_handlers import handle_xblock
from cms.djangoapps.api.v1.serializers.course_runs import CourseRunCreateSerializer, CourseRunSerializer
from cms.djangoapps.contentstore.views.course import get_course_and_check_access
from xmodule.modulestore.django import modulestore
from xmodule.modulestore.exceptions import DuplicateCourseError


@api_view(['DELETE', 'GET', 'PUT', 'POST', 'PATCH'])
@authentication_classes([
    JwtAuthentication,
    OAuth2AuthenticationAllowInactiveUser,
    BearerAuthenticationAllowInactiveUser,
])
@permission_classes([IsAuthenticated])
def mx_xblock_handler(request, usage_key_string=None):
    # Replicate what @expect_json does — handle_xblock reads request.json, not request.data.
    if not hasattr(request, 'json'):
        try:
            request.json = json.loads(request.body.decode('utf-8')) if request.body else {}
        except ValueError:
            return Response({'error': 'Invalid JSON'}, status=400)

    # Delegate entirely to the original handler — access checks, branch logic,
    # create/update/delete are all handled inside handle_xblock unchanged.
    django_response = handle_xblock(request, usage_key_string)

    # Convert Django HttpResponse → DRF Response.
    try:
        data = json.loads(django_response.content) if django_response.content else None
    except (ValueError, AttributeError):
        data = None

    return Response(data, status=django_response.status_code)


_AUTH_CLASSES = [
    JwtAuthentication,
    OAuth2AuthenticationAllowInactiveUser,
    BearerAuthenticationAllowInactiveUser,
]


@api_view(['POST'])
@authentication_classes(_AUTH_CLASSES)
@permission_classes([IsAuthenticated])
def mx_course_run_create(request):
    """
    POST /api/v1/mx_course_runs/

    Creates a new course run. Requires staff access.
    Returns 409 with course details if the course already exists.
    Returns 201 with course details on successful creation.
    Both responses include the block locator (location field).
    """
    if not request.user.is_staff:
        return Response({'error': 'Staff access required.'}, status=status.HTTP_403_FORBIDDEN)

    serializer = CourseRunCreateSerializer(data=request.data, context={'request': request})
    serializer.is_valid(raise_exception=True)

    try:
        course_run = serializer.save()
    except DuplicateCourseError:
        _id = serializer.validated_data['id']
        course_key = modulestore().make_course_key(_id['org'], _id['course'], _id['run'])
        course_run = get_course_and_check_access(course_key, request.user)
        course_data = CourseRunSerializer(course_run, context={'request': request}).data
        course_data['locator_id'] = str(course_run.location)
        course_data['created_at'] = course_run.edited_on
        return Response(
            {'message': 'A course with this org/number/run already exists.', 'course': course_data},
            status=status.HTTP_409_CONFLICT,
        )
    except ValidationError as exc:
        # create_new_course (edx-platform) checks org+course number (ignoring run)
        # before modulestore ever gets a chance to raise DuplicateCourseError, so
        # this fires even for an exact org/number/run duplicate. Surface the
        # conflicting course either way, with a message that reflects which case it is.
        _id = serializer.validated_data['id']
        org, number, run = _id['org'], _id['course'], _id['run']
        existing_course = next(
            (c for c in CourseOverview.objects.filter(org=org) if c.id.course == number),
            None,
        )
        if existing_course is None:
            raise

        is_exact_duplicate = existing_course.id.run == run
        message = (
            'A course with this org/number/run already exists.'
            if is_exact_duplicate else str(exc.detail[0])
        )

        course_run = get_course_and_check_access(existing_course.id, request.user)
        course_data = CourseRunSerializer(course_run, context={'request': request}).data
        course_data['locator_id'] = str(course_run.location)
        course_data['created_at'] = course_run.edited_on
        return Response(
            {'message': message, 'course': course_data},
            status=status.HTTP_409_CONFLICT,
        )

    course_data = CourseRunSerializer(course_run, context={'request': request}).data
    course_data['locator_id'] = str(course_run.location)
    course_data['created_at'] = course_run.edited_on
    return Response(
        {'message': 'Course successfully created.', 'course': course_data},
        status=status.HTTP_201_CREATED,
    )


@api_view(['PUT', 'PATCH', 'POST'])
@authentication_classes(_AUTH_CLASSES)
@permission_classes([IsAuthenticated])
def mx_course_run_update(request, course_key_string):
    """
    PUT/PATCH/POST /api/v1/mx_course_runs/<course_id>/

    Updates an existing course run's title and/or schedule (start, end,
    enrollment_start, enrollment_end). Requires staff access.
    POST is accepted as an alias for PATCH, for clients that can't send PUT/PATCH.
    """
    if not request.user.is_staff:
        return Response({'error': 'Staff access required.'}, status=status.HTTP_403_FORBIDDEN)

    # Some clients/proxies decode '+' as a space in URL path segments too;
    # course IDs use '+' as a separator, so restore it here (mirrors get_course_content).
    course_id_param = course_key_string.strip().replace(' ', '+')
    try:
        course_key = CourseKey.from_string(course_id_param)
    except InvalidKeyError:
        return Response(
            {'error': f'Invalid course_id: {course_id_param}'},
            status=status.HTTP_400_BAD_REQUEST,
        )

    course_run = get_course_and_check_access(course_key, request.user)
    if not course_run:
        return Response(
            {'error': f'Course not found: {course_id_param}'},
            status=status.HTTP_404_NOT_FOUND,
        )

    partial = request.method in ('PATCH', 'POST')
    serializer = CourseRunSerializer(
        course_run, data=request.data, partial=partial, context={'request': request},
    )
    serializer.is_valid(raise_exception=True)
    serializer.save()

    # Re-fetch so edited_on reflects the just-saved change rather than a stale in-memory value.
    course_run = get_course_and_check_access(course_key, request.user)
    try:
        created_at = CourseOverview.objects.get(id=course_key).created
    except CourseOverview.DoesNotExist:
        created_at = None

    course_data = CourseRunSerializer(course_run, context={'request': request}).data
    course_data['locator_id'] = str(course_run.location)
    course_data['created_at'] = created_at
    course_data['updated_at'] = course_run.edited_on
    return Response(
        {'message': 'Course successfully updated.', 'course': course_data},
        status=status.HTTP_200_OK,
    )
