from django.contrib import admin
from reviews.models.rating_models import MasterRating, Rating

# Rating modeli üçün admin konfiqurasiyası
class RatingAdmin(admin.ModelAdmin):
    list_display = ('master', 'user', 'rating', 'created_at')
    search_fields = ('master__full_name', 'user')
    list_filter = ('rating', 'created_at')
    readonly_fields = ('created_at',)
    ordering = ('-created_at',)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related('master')

# MasterRating modeli üçün admin konfiqurasiyası
class MasterRatingAdmin(admin.ModelAdmin):
    list_display = ('master', 'average_rating', 'rating_count')
    search_fields = ('master__full_name',)
    readonly_fields = ('average_rating', 'rating_count')
    ordering = ('-average_rating',)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related('master')

# Modelləri admin paneldə qeydiyyatdan keçirmək
admin.site.register(Rating, RatingAdmin)
admin.site.register(MasterRating, MasterRatingAdmin)