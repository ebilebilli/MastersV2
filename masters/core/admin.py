from django.contrib import admin
from core.models.city_model import City, District
from core.models.education_model import Education
from core.models.language_model import Language


class CityAdmin(admin.ModelAdmin):
    list_display = ('display_name', 'name')
    search_fields = ('name', 'display_name')
    ordering = ('display_name',)

class DistrictAdmin(admin.ModelAdmin):
    list_display = ('display_name', 'name', 'city')
    search_fields = ('name', 'display_name')
    list_filter = ('city',)
    ordering = ('display_name',)


class EducationAdmin(admin.ModelAdmin):
    list_display = ('display_name', 'name')
    search_fields = ('name', 'display_name')
    ordering = ('display_name',)


class LanguageAdmin(admin.ModelAdmin):
    list_display = ('display_name', 'name')
    search_fields = ('name', 'display_name')
    ordering = ('display_name',)


# Adminə qeydiyyat
admin.site.register(City, CityAdmin)
admin.site.register(District, DistrictAdmin)
admin.site.register(Education, EducationAdmin)
admin.site.register(Language, LanguageAdmin)

