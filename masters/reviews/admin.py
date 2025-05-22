from django.contrib import admin
from reviews.models.rating_models import MasterRating, Rating


@admin.register(Rating)
class RatingAdmin(admin.ModelAdmin):
    list_display = ('master_full_name', 'user', 'rating', 'created_at')
    search_fields = ('master__full_name', 'user')
    list_filter = ('rating', 'created_at')
    readonly_fields = ('created_at',)
    ordering = ('-created_at',)
    list_select_related = ('master',)

    def master_full_name(self, obj):
        return obj.master.full_name
    master_full_name.admin_order_field = 'master__full_name'
    master_full_name.short_description = 'Master'

    # Optional: Add ability to bulk delete or other admin actions
    actions = ['delete_selected']


