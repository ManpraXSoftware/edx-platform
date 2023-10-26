"""
django admin pages for program support models
"""


from config_models.admin import ConfigurationModelAdmin
from django.contrib import admin

from openedx.core.djangoapps.programs.models import ProgramsApiConfig, CustomProgramsConfig, LastReadCourse


class ProgramsApiConfigAdmin(ConfigurationModelAdmin):
    pass


class LastReadCourseAdmin(admin.ModelAdmin):
    pass


admin.site.register(ProgramsApiConfig, ProgramsApiConfigAdmin)
admin.site.register(CustomProgramsConfig, ConfigurationModelAdmin)
admin.site.register(LastReadCourse, LastReadCourseAdmin)
