"""
Serializer for user API
"""


from rest_framework import serializers
from rest_framework.reverse import reverse

from common.djangoapps.course_modes.models import CourseMode
from common.djangoapps.student.models import CourseEnrollment, User
from common.djangoapps.util.course import get_encoded_course_sharing_utm_params, get_link_for_about_page
from lms.djangoapps.certificates.api import certificate_downloadable_status
from lms.djangoapps.courseware.access import has_access
from openedx.features.course_duration_limits.access import get_user_course_expiration_date


class CourseOverviewField(serializers.RelatedField):  # lint-amnesty, pylint: disable=abstract-method
    """
    Custom field to wrap a CourseOverview object. Read-only.
    """
    def to_representation(self, course_overview):  # lint-amnesty, pylint: disable=arguments-differ
        course_id = str(course_overview.id)
        request = self.context.get('request')
        api_version = self.context.get('api_version')
        enrollment = CourseEnrollment.get_enrollment(user=self.context.get('request').user, course_key=course_id)
        return {
            # identifiers
            'id': course_id,
            'name': course_overview.display_name,
            'number': course_overview.display_number_with_default,
            'org': course_overview.display_org_with_default,

            # dates
            'start': course_overview.start,
            'start_display': course_overview.start_display,
            'start_type': course_overview.start_type,
            'end': course_overview.end,
            'dynamic_upgrade_deadline': enrollment.upgrade_deadline,

            # notification info
            'subscription_id': course_overview.clean_id(padding_char='_'),

            # access info
            'courseware_access': has_access(
                request.user,
                'load_mobile',
                course_overview
            ).to_json(),

            # various URLs
            # course_image is sent in both new and old formats
            # (within media to be compatible with the new Course API)
            'media': {
                'course_image': {
                    'uri': course_overview.course_image_url,
                    'name': 'Course Image',
                }
            },
            'course_image': course_overview.course_image_url,
            'course_about': get_link_for_about_page(course_overview),
            'course_sharing_utm_parameters': get_encoded_course_sharing_utm_params(),
            'course_updates': reverse(
                'course-updates-list',
                kwargs={'api_version': api_version, 'course_id': course_id},
                request=request,
            ),
            'course_handouts': reverse(
                'course-handouts-list',
                kwargs={'api_version': api_version, 'course_id': course_id},
                request=request,
            ),
            'discussion_url': reverse(
                'discussion_course',
                kwargs={'course_id': course_id},
                request=request,
            ) if course_overview.is_discussion_tab_enabled(request.user) else None,

            # This is an old API that was removed as part of DEPR-4. We keep the
            # field present in case API parsers expect it, but this API is now
            # removed.
            'video_outline': None,

            'is_self_paced': course_overview.self_paced
        }


class CourseEnrollmentSerializer(serializers.ModelSerializer):
    """
    Serializes CourseEnrollment models
    """
    course = CourseOverviewField(source="course_overview", read_only=True)
    certificate = serializers.SerializerMethodField()
    audit_access_expires = serializers.SerializerMethodField()
    course_modes = serializers.SerializerMethodField()

    def get_audit_access_expires(self, model):
        """
        Returns expiration date for a course audit expiration, if any or null
        """
        return get_user_course_expiration_date(model.user, model.course)

    def get_certificate(self, model):
        """Returns the information about the user's certificate in the course."""
        certificate_info = certificate_downloadable_status(model.user, model.course_id)
        if certificate_info['is_downloadable']:
            return {
                'url': self.context['request'].build_absolute_uri(
                    certificate_info['download_url']
                ),
            }
        else:
            return {}

    def get_course_modes(self, obj):
        """
        Retrieve course modes associated with the course.
        """
        course_modes = CourseMode.modes_for_course(
            obj.course.id,
            only_selectable=False
        )
        return [
            ModeSerializer(mode).data
            for mode in course_modes
        ]

    class Meta:
        model = CourseEnrollment
        fields = ('audit_access_expires', 'created', 'mode', 'is_active', 'course', 'certificate', 'course_modes')
        lookup_field = 'username'


class CourseEnrollmentSerializerv05(CourseEnrollmentSerializer):
    """
    Serializes CourseEnrollment models for v0.5 api
    Does not include 'audit_access_expires' field that is present in v1 api
    """
    class Meta:
        model = CourseEnrollment
        fields = ('created', 'mode', 'is_active', 'course', 'certificate')
        lookup_field = 'username'


class UserSerializer(serializers.ModelSerializer):
    """
    Serializes User models
    """
    name = serializers.ReadOnlyField(source='profile.name')
    course_enrollments = serializers.SerializerMethodField()
    mobile_number = serializers.SerializerMethodField()
    classes_taught = serializers.SerializerMethodField()
    tag_label = serializers.SerializerMethodField()
    school = serializers.SerializerMethodField()
    board = serializers.SerializerMethodField()
    medium = serializers.SerializerMethodField()
    dob = serializers.SerializerMethodField()
    you_want_see_inthis_app = serializers.SerializerMethodField()
    association_with_bhartifound = serializers.SerializerMethodField()
    state = serializers.ReadOnlyField(source='profile.state')
    gender = serializers.ReadOnlyField(source='profile.gender')
    organisation = serializers.SerializerMethodField()
    role = serializers.SerializerMethodField()
    pincode = serializers.SerializerMethodField()
    receive_update_on_whatsapp = serializers.SerializerMethodField()
    is_google = serializers.SerializerMethodField()

    def get_course_enrollments(self, model):
        request = self.context.get('request')
        api_version = self.context.get('api_version')

        return reverse(
            'courseenrollment-detail',
            kwargs={'api_version': api_version, 'username': model.username},
            request=request
        )
    def get_mobile_number(self, model):
        mobile_number = self.context.get('mobile_number')
        return mobile_number
    def get_classes_taught(self, model):
        classes_taught = self.context.get('classes_taught')
        return classes_taught

    def get_tag_label(self, model):
        tag_label = self.context.get('tag_label')
        return tag_label

    def get_is_google(self, model):
        is_google = self.context.get('is_google')
        return is_google

    def get_board(self, model):
        board = self.context.get('board')
        return board
    
    def get_school(self, model):
        board = self.context.get('school')
        return board

    def get_medium(self, model):
        medium = self.context.get('medium')
        return medium

    def get_dob(self, model):
        dob = self.context.get('dob')
        return dob
    def get_you_want_see_inthis_app(self, model):
        you_want_see_inthis_app = self.context.get('you_want_see_inthis_app')
        return you_want_see_inthis_app

    def get_association_with_bhartifound(self, model):
        association_with_bhartifound = self.context.get('association_with_bhartifound')
        return association_with_bhartifound

    def get_organisation(self, model):
        organisation = self.context.get("organisation")
        return organisation

    def get_role(self,model):
        role = self.context['role']
        return role

    def get_pincode(self,model):
        pincode = self.context["pincode"]
        return pincode

    def get_receive_update_on_whatsapp(self,model):
        receive_update_on_whatsapp=self.context['receive_update_on_whatsapp']
        return receive_update_on_whatsapp
    class Meta:
        model = User
        fields = ('id', 'username', 'mobile_number', 'email', 'name', 'course_enrollments','classes_taught','school','state',
                  'tag_label','gender','board','medium','dob','you_want_see_inthis_app','association_with_bhartifound',
                  'organisation', 'receive_update_on_whatsapp', 'role', 'pincode',"is_google")
        lookup_field = 'username'
        # For disambiguating within the drf-yasg swagger schema
        ref_name = 'mobile_api.User'


class ModeSerializer(serializers.Serializer):  # pylint: disable=abstract-method
    """
    Serializes a course's 'Mode' tuples

    Returns a serialized representation of the modes available for course enrollment. The course
    modes models are designed to return a tuple instead of the model object itself. This serializer
    handles the given tuple.

    """
    slug = serializers.CharField(max_length=100)
    sku = serializers.CharField()
    android_sku = serializers.CharField()
    ios_sku = serializers.CharField()
    min_price = serializers.IntegerField()
