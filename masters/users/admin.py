from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from users.models.master_model import Master
from users.models.master_work_img_model import MasterWorkImage


class MasterAdmin(UserAdmin):
    # Admin paneldə göstəriləcək sahələr
    list_display = (
        'full_name', 'phone_number', 'profession_category', 'profession_service',
        'is_active_on_main_page', 'is_active', 'date_joined'
    )
    
    # Axtarış üçün sahələr
    search_fields = ('full_name', 'phone_number', 'email')
    
    # Filtrləmə üçün sahələr
    list_filter = (
        'profession_category', 'profession_service', 'cities', 'districts',
        'gender', 'is_active_on_main_page', 'is_active'
    )
    
    # Admin formasında göstəriləcək sahələr və qruplar
    fieldsets = (
        (None, {
            'fields': ('phone_number', 'password')
        }),
        ('Şəxsi məlumatlar', {
            'fields': (
                'full_name', 'birthday', 'gender',
                'profile_picture'
            )
        }),
        ('Peşə məlumatları', {
            'fields': (
                'profession_category', 'profession_service', 'custom_profession',
                'experience', 'cities', 'districts'
            )
        }),
        ('Təhsil və dillər', {
            'fields': ('education', 'education_detail', 'languages')
        }),
        ('Əlavə məlumatlar', {
            'fields': (
                'note', 'facebook_url', 'instagram_url', 'tiktok_url',
                'linkedin_url', 'youtube_url'
            )
        }),
        ('İcazələr', {
            'fields': ('is_active_on_main_page', 'is_active', 'is_staff', 'is_superuser')
        }),
    )
    
    # Yeni istifadəçi əlavə edərkən göstəriləcək sahələr
    add_fieldsets = (
    (None, {
        'classes': ('wide',),
        'fields': (
            'phone_number', 'password1', 'password2', 'full_name',
            'birthday', 'gender', 'profession_category', 'profession_service',
            'cities', 'districts', 'education', 'languages', 'is_active_on_main_page'
        )
    }),
)
    
    # Çox-çox əlaqələr üçün filtrlənmiş widget
    filter_horizontal = ('cities', 'districts', 'languages')
    
    # Sıralama
    ordering = ('full_name',)
    
    # Modeldəki məlumatların redaktəsi üçün readonly sahələr (məsələn, tarixlər)
    readonly_fields = ('date_joined',)

class MasterWorkImageAdmin(admin.ModelAdmin):
    list_display = ('get_master_name', 'image', 'uploaded_at')
    search_fields = ('master__full_name',)
    list_filter = ('uploaded_at',)
    readonly_fields = ('uploaded_at',)
    ordering = ('-uploaded_at',)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related('master')

    def get_master_name(self, obj):
        return obj.master.full_name
    get_master_name.short_description = 'Usta adı'


admin.site.register(Master, MasterAdmin)
admin.site.register(MasterWorkImage, MasterWorkImageAdmin)