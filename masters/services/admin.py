from django.contrib import admin
from services.models.category_model import Category
from services.models.service_model import Service

# Category modeli üçün admin konfiqurasiyası
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('display_name', 'name')
    search_fields = ('name', 'display_name')
    ordering = ('display_name',)

# ServiceTemplate modeli üçün admin konfiqurasiyası
class ServiceAdmin(admin.ModelAdmin):
    list_display = ('display_name', 'name', 'category')
    search_fields = ('name', 'display_name', 'category__name')
    list_filter = ('category',)
    ordering = ('display_name',)

# Modelləri admin paneldə qeydiyyatdan keçirmək
admin.site.register(Category, CategoryAdmin)
admin.site.register(Service, ServiceAdmin)