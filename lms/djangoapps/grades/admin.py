"""
Django admin page for grades models
"""


from config_models.admin import ConfigurationModelAdmin
from django.contrib import admin

from lms.djangoapps.grades.config.models import (
    ComputeGradesSetting
)
from  .models import PersistentCourseGrade

admin.site.register(ComputeGradesSetting, ConfigurationModelAdmin)


@admin.register(PersistentCourseGrade)
class PersistentCourseGradeAdmin(admin.ModelAdmin):
    list_display = ('user_id', 'course_id', 'percent_grade',)
    list_filter = ('course_id',)
    search_fields = ('user_id', 'course_id',)

