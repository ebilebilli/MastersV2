from django.contrib import admin
from reviews.models.review_models import Review
from reviews.models.review_img_model import ReviewWorkImage


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'master',
        'username',
        'rating',
        'created_at',
        'updated_at',
    )
    list_filter = ('rating', 'created_at')
    search_fields = ('username', 'user', 'comment')
    readonly_fields = ('created_at', 'updated_at')

    fieldsets = (
        ('Əsas məlumatlar', {
            'fields': ('master', 'user', 'username', 'rating', 'comment')
        }),
        ('Dəyərləndirmə kriteriyaları', {
            'fields': (
                'responsible', 'neat', 'time_management', 'communicative',
                'punctual', 'professional', 'experienced', 'efficient',
                'agile', 'patient'
            ),
            'classes': ('collapse',),
        }),
        ('Tarix məlumatları', {
            'fields': ('created_at', 'updated_at'),
        }),
    )


@admin.register(ReviewWorkImage)
class ReviewWorkImageAdmin(admin.ModelAdmin):
    list_display = ('id', 'review', 'image_tag', 'order', 'is_active', 'uploaded_at')
    list_filter = ('is_active', 'uploaded_at')
    search_fields = ('review__username', 'review__user')
    readonly_fields = ('uploaded_at', 'image_preview')

    def image_tag(self, obj):
        if obj.image:
            return f'<img src="{obj.image.url}" width="80" height="80" style="object-fit: cover;" />'
        return "-"
    image_tag.allow_tags = True
    image_tag.short_description = 'Şəkil'

    def image_preview(self, obj):
        return self.image_tag(obj)
    image_preview.allow_tags = True
    image_preview.short_description = "Şəkil Önizləmə"