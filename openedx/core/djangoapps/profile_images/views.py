"""
This module implements the upload and remove endpoints of the profile image api.
"""


import datetime
import itertools
import logging
from contextlib import closing

from django.utils.translation import gettext as _
from edx_rest_framework_extensions.auth.jwt.authentication import JwtAuthentication
from edx_rest_framework_extensions.auth.session.authentication import SessionAuthenticationAllowInactiveUser
from pytz import UTC
from rest_framework import permissions, status
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.response import Response
from rest_framework.views import APIView

from openedx.core.djangoapps.user_api.accounts.image_helpers import get_profile_image_names, set_has_profile_image
from openedx.core.djangoapps.user_api.errors import UserNotFound
from openedx.core.lib.api.authentication import BearerAuthenticationAllowInactiveUser
from openedx.core.lib.api.parsers import TypedFileUploadParser
from openedx.core.lib.api.permissions import IsUserInUrl
from openedx.core.lib.api.view_utils import DeveloperErrorViewMixin

from .exceptions import ImageValidationError
from .images import IMAGE_TYPES, create_profile_images, remove_profile_images, validate_uploaded_image

log = logging.getLogger(__name__)

LOG_MESSAGE_CREATE = 'Generated and uploaded images %(image_names)s for user %(user_id)s'
LOG_MESSAGE_DELETE = 'Deleted images %(image_names)s for user %(user_id)s'


def _make_upload_dt():
    """
    Generate a server-side timestamp for the upload. This is in a separate
    function so its behavior can be overridden in tests.
    """
    return datetime.datetime.utcnow().replace(tzinfo=UTC)


class ProfileImageView(DeveloperErrorViewMixin, APIView):
    """
    **Use Cases**

        Add or remove profile images associated with user accounts.

        The requesting user must be signed in.  Users can only add profile
        images to their own account.  Users with staff access can remove
        profile images for other user accounts.  All other users can remove
        only their own profile images.

    **Example Requests**

        POST /api/user/v1/accounts/{username}/image

        DELETE /api/user/v1/accounts/{username}/image

    **Example POST Responses**

        When the requesting user attempts to upload an image for their own
        account, the request returns one of the following responses:

        * If the upload could not be performed, the request returns an HTTP 400
          "Bad Request" response with information about why the request failed.

        * If the upload is successful, the request returns an HTTP 204 "No
          Content" response with no additional content.

        If the requesting user tries to upload an image for a different
        user, the request returns one of the following responses:

        * If no user matches the "username" parameter, the request returns an
          HTTP 404 "Not Found" response.

        * If the user whose profile image is being uploaded exists, but the
          requesting user does not have staff access, the request returns an
          HTTP 404 "Not Found" response.

        * If the specified user exists, and the requesting user has staff
          access, the request returns an HTTP 403 "Forbidden" response.

    **Example DELETE Responses**

        When the requesting user attempts to remove the profile image for
        their own account, the request returns one of the following
        responses:

        * If the image could not be removed, the request returns an HTTP 400
          "Bad Request" response with information about why the request failed.

        * If the request successfully removes the image, the request returns
          an HTTP 204 "No Content" response with no additional content.

        When the requesting user tries to remove the profile image for a
        different user, the view will return one of the following responses:

        * If the requesting user has staff access, and the "username" parameter
          matches a user, the profile image for the specified user is deleted,
          and the request returns an HTTP 204 "No Content" response with no
          additional content.

        * If the requesting user has staff access, but no user is matched by
          the "username" parameter, the request returns an HTTP 404 "Not Found"
          response.

        * If the requesting user does not have staff access, the request
          returns an HTTP 404 "Not Found" response, regardless of whether
          the user exists or not.
    """

    parser_classes = (MultiPartParser, FormParser, TypedFileUploadParser)
    authentication_classes = (
        JwtAuthentication,
        BearerAuthenticationAllowInactiveUser,
        SessionAuthenticationAllowInactiveUser,
    )
    permission_classes = (permissions.IsAuthenticated, IsUserInUrl)

    upload_media_types = set(itertools.chain(*(image_type.mimetypes for image_type in IMAGE_TYPES.values())))

    
    def post(self, request, username):
        """
        POST /api/user/v1/accounts/{username}/image
        """
        from django.http.request import UnreadablePostError
        # Log initial request details
        log.info(f"Request content-type: {request.content_type}")
        log.info(f"User agent: {request.META.get('HTTP_USER_AGENT', 'Unknown')})")
        log.info(f"Content-Length: {request.META.get('CONTENT_LENGTH', 'Unknown')})")
        log.info(f"Request headers: {dict(request.META)}")

        # Validate content type
        if 'multipart/form-data' not in request.content_type.lower():
            log.error(f"Invalid content type: {request.content_type}")
            return Response(
                {
                    "developer_message": "Request must be multipart/form-data",
                    "user_message": _("Please upload the image using a multipart form data"),
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Validate file size
        content_length = request.META.get('CONTENT_TYPE', '0')
        try:
            content_length = int(content_length)
            if content_length > 10 * 1024 * 1024:  # 10MB limit (increased from 5MB)
                log.error(f"File size too large: {content_length} bytes")
                return Response(
                    {
                        "developer_message": f"File size {content_length} bytes exceeds 10MB limit",
                        "user_message": _("Image file is too large. Please upload a file smaller than 10MB."),
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )
        except ValueError:
            log.error(f"Invalid Content-Length: {content_length}")
            return Response(
                {
                    "developer_message": "Invalid Content-Length header",
                    "user_message": _("Invalid request format"),
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        # Attempt to parse request data
        try:
            parsed_data = request.data
            log.info(f"Parsed request data: {parsed_data}")
        except UnreadablePostError as e:
            log.error(f"UnreadablePostError parsing request data: {str(e)}")
            return Response(
                {
                    "developer_message": f"Failed to read request body: {str(e)}. Likely caused by middleware reading the body prematurely.",
                    "user_message": _("Failed to upload image. Please try again or use a smaller file."),
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            log.error(f"Error parsing request data: {str(e)}")
            return Response(
                {
                    "developer_message": f"Failed to parse request: {str(e)}",
                    "user_message": _("Invalid request format"),
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        # Log request.FILES
        try:
            log.info(f"Request files: {request.FILES}")
        except Exception as e:
            log.error(f"Error accessing request.FILES: {str(e)}")
            return Response(
                {
                    "developer_message": f"Failed to access files: {str(e)}",
                    "user_message": _("Invalid file upload"),
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        # Check for file in request.FILES
        if 'file' not in request.FILES:
            log.error("No file provided in request.FILES")
            return Response(
                {
                    "developer_message": "No file provided for profile image",
                    "user_message": _("No file provided for profile image"),
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        # Process the upload
        uploaded_file = request.FILES['file']
        with closing(uploaded_file):
            # Image file validation
            try:
                validate_uploaded_image(uploaded_file)
            except ImageValidationError as error:
                log.error(f"Image validation failed: {str(error)}")
                return Response(
                    {
                        "developer_message": str(error),
                        "user_message": error.user_message
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Generate profile pic and thumbnails
            try:
                profile_image_names = get_profile_image_names(username)
                create_profile_images(uploaded_file, profile_image_names)
                set_has_profile_image(username, True, _make_upload_dt())
                log.info(
                    LOG_MESSAGE_CREATE,
                    {'image_names': list(profile_image_names.values()), 'user_id': request.user.id}
                )
            except Exception as e:
                log.error(f"Error processing image: {str(e)}")
                return Response(
                    {
                        "developer_message": f"Failed to process image: {str(e)}",
                        "user_message": _("Failed to process image"),
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )

        return Response(status=status.HTTP_204_NO_CONTENT)

    # def post(self, request, username):
    #     """
    #     POST /api/user/v1/accounts/{username}/image
    #     """
    #     # Log initial request details
    #     log.info(f"Request content-type: {request.content_type}")
    #     log.info(f"User agent: {request.META.get('HTTP_USER_AGENT', 'Unknown')}")

    #     # Validate content type
    #     if 'multipart/form-data' not in request.content_type.lower():
    #         log.error(f"Invalid content type: {request.content_type}")
    #         return Response(
    #             {
    #                 "developer_message": "Request must be multipart/form-data",
    #                 "user_message": _("Please upload the image using a multipart form"),
    #             },
    #             status=status.HTTP_400_BAD_REQUEST
    #         )

    #     # Force parsing of the request body immediately
    #     try:
    #         # Access request.data to trigger parsing by DRF parsers
    #         parsed_data = request.data
    #         log.info(f"Parsed request data: {parsed_data}")
    #     except Exception as e:
    #         log.error(f"Error parsing request data: {str(e)}")
    #         return Response(
    #             {
    #                 "developer_message": f"Failed to parse request: {str(e)}",
    #                 "user_message": _("Invalid request format"),
    #             },
    #             status=status.HTTP_400_BAD_REQUEST
    #         )

    #     # Log request.FILES after parsing
    #     try:
    #         log.info(f"Request files: {request.FILES}")
    #     except Exception as e:
    #         log.error(f"Error accessing request.FILES: {str(e)}")
    #         return Response(
    #             {
    #                 "developer_message": f"Failed to access files: {str(e)}",
    #                 "user_message": _("Invalid file upload"),
    #             },
    #             status=status.HTTP_400_BAD_REQUEST
    #         )

    #     # Check for file in request.FILES
    #     if 'file' not in request.FILES:
    #         log.error("No file provided in request.FILES")
    #         return Response(
    #             {
    #                 "developer_message": "No file provided for profile image",
    #                 "user_message": _("No file provided for profile image"),
    #             },
    #             status=status.HTTP_400_BAD_REQUEST
    #         )

    #     # Process the upload
    #     uploaded_file = request.FILES['file']
    #     with closing(uploaded_file):
    #         # Image file validation
    #         try:
    #             validate_uploaded_image(uploaded_file)
    #         except ImageValidationError as error:
    #             log.error(f"Image validation failed: {str(error)}")
    #             return Response(
    #                 {
    #                     "developer_message": str(error),
    #                     "user_message": error.user_message
    #                 },
    #                 status=status.HTTP_400_BAD_REQUEST
    #             )

    #         # Generate profile pic and thumbnails and store them
    #         try:
    #             profile_image_names = get_profile_image_names(username)
    #             create_profile_images(uploaded_file, profile_image_names)
    #             set_has_profile_image(username, True, _make_upload_dt())
    #             log.info(
    #                 LOG_MESSAGE_CREATE,
    #                 {'image_names': list(profile_image_names.values()), 'user_id': request.user.id}
    #             )
    #         except Exception as e:
    #             log.error(f"Error processing image: {str(e)}")
    #             return Response(
    #                 {
    #                     "developer_message": f"Failed to process image: {str(e)}",
    #                     "user_message": _("Failed to process image"),
    #                 },
    #                 status=status.HTTP_400_BAD_REQUEST
    #             )

    #     return Response(status=status.HTTP_204_NO_CONTENT)
    
    # def mx_post(self, request, username):
    #     """
    #     POST /api/user/v1/accounts/{username}/image
    #     """

    #     log.info(f"Request content-type: {request.content_type}")
    #     log.info(f"Request files: {request.FILES}")
    #     log.info(f"Request data: {request.data}")
    #     log.info(f"User agent: {request.META.get('HTTP_USER_AGENT', 'Unknown')}")

    #     # Validate content type
    #     if 'multipart/form-data' not in request.content_type.lower():
    #         log.error(f"Invalid content type: {request.content_type}")
    #         return Response(
    #             {
    #                 "developer_message": "Request must be multipart/form-data",
    #                 "user_message": _("Please upload the image using a multipart form"),
    #             },
    #             status=status.HTTP_400_BAD_REQUEST
    #         )

    #     # Force parsing of the request to load FILES and data
    #     try:
    #         # Access request.data to trigger parsing
    #         if not request.data:
    #             log.error("No data parsed from request")
    #             return Response(
    #                 {
    #                     "developer_message": "No data parsed from request",
    #                     "user_message": _("Invalid or empty request data"),
    #                 },
    #                 status=status.HTTP_400_BAD_REQUEST
    #             )
    #     except Exception as e:
    #         log.error(f"Error parsing request: {str(e)}")
    #         return Response(
    #             {
    #                 "developer_message": f"Failed to parse request: {str(e)}",
    #                 "user_message": _("Invalid request format"),
    #             },
    #             status=status.HTTP_400_BAD_REQUEST
    #         )
        
    #     # validate request:
    #     # verify that the user's
    #     # ensure any file was sent
    #     if 'file' not in request.FILES:
    #         return Response(
    #             {
    #                 "developer_message": "No file provided for profile image",
    #                 "user_message": _("No file provided for profile image"),

    #             },
    #             status=status.HTTP_400_BAD_REQUEST
    #         )

    #     # process the upload.
    #     uploaded_file = request.FILES['file']

    #     # no matter what happens, delete the temporary file when we're done
    #     with closing(uploaded_file):

    #         # image file validation.
    #         try:
    #             validate_uploaded_image(uploaded_file)
    #         except ImageValidationError as error:
    #             return Response(
    #                 {"developer_message": str(error), "user_message": error.user_message},
    #                 status=status.HTTP_400_BAD_REQUEST,
    #             )

    #         # generate profile pic and thumbnails and store them
    #         profile_image_names = get_profile_image_names(username)
    #         create_profile_images(uploaded_file, profile_image_names)

    #         # update the user account to reflect that a profile image is available.
    #         set_has_profile_image(username, True, _make_upload_dt())

    #         log.info(
    #             LOG_MESSAGE_CREATE,
    #             {'image_names': list(profile_image_names.values()), 'user_id': request.user.id}
    #         )

    #     # send client response.
    #     return Response(status=status.HTTP_204_NO_CONTENT)

    def delete(self, request, username):
        """
        DELETE /api/user/v1/accounts/{username}/image
        """

        try:
            # update the user account to reflect that the images were removed.
            set_has_profile_image(username, False)

            # remove physical files from storage.
            profile_image_names = get_profile_image_names(username)
            remove_profile_images(profile_image_names)

            log.info(
                LOG_MESSAGE_DELETE,
                {'image_names': list(profile_image_names.values()), 'user_id': request.user.id}
            )
        except UserNotFound:
            return Response(status=status.HTTP_404_NOT_FOUND)

        # send client response.
        return Response(status=status.HTTP_204_NO_CONTENT)


class ProfileImageUploadView(APIView):
    """
    **DEPRECATION WARNING**

        /api/profile_images/v1/{username}/upload is deprecated.
        All requests should now be sent to
        /api/user/v1/accounts/{username}/image
    """

    parser_classes = ProfileImageView.parser_classes
    authentication_classes = ProfileImageView.authentication_classes
    permission_classes = ProfileImageView.permission_classes

    def post(self, request, username):
        """
        POST /api/profile_images/v1/{username}/upload
        """
        return ProfileImageView().post(request, username)


class ProfileImageRemoveView(APIView):
    """
    **DEPRECATION WARNING**

        /api/profile_images/v1/{username}/remove is deprecated.
        This endpoint's POST is replaced by the DELETE method at
        /api/user/v1/accounts/{username}/image.
    """

    authentication_classes = ProfileImageView.authentication_classes
    permission_classes = ProfileImageView.permission_classes

    def post(self, request, username):
        """
        POST /api/profile_images/v1/{username}/remove
        """
        return ProfileImageView().delete(request, username)
