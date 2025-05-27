from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from django.core.validators import FileExtensionValidator
from users.models import Master
from core.models.city_model import City, District
from core.models.education_model import Education
from core.models.language_model import Language
from services.models.category_model import Category
from services.models.service_model import ServiceTemplate

class MasterSerializer(serializers.ModelSerializer):
    # Şəxsi məlumatlar
    full_name = serializers.CharField(max_length=50, required=True)
    birthday = serializers.DateField(required=True)
    phone_number = serializers.CharField(max_length=13, required=True)
    password = serializers.CharField(write_only=True, required=True)
    password2 = serializers.CharField(write_only=True, required=True, label="Şifrəni təkrar yazın")
    gender = serializers.ChoiceField(choices=Master.GENDER_STATUS, required=True)

    # Peşə məlumatları
    profession_category = serializers.PrimaryKeyRelatedField(queryset=Category.objects.all(), required=True, allow_null=False)
    profession_service = serializers.PrimaryKeyRelatedField(queryset=ServiceTemplate.objects.all(), required=True, allow_null=False)
    custom_profession = serializers.CharField(max_length=100, required=False, allow_blank=True, allow_null=True)
    experience = serializers.IntegerField(required=True, min_value=0)
    cities = serializers.PrimaryKeyRelatedField(many=True, queryset=City.objects.all(), required=True, allow_null=False)
    districts = serializers.PrimaryKeyRelatedField(many=True, queryset=District.objects.all(), required=False, allow_null=False)
    education = serializers.PrimaryKeyRelatedField(queryset=Education.objects.all(), required=True, allow_null=False)
    education_detail = serializers.CharField(max_length=50, required=False, allow_blank=True, allow_null=True)
    languages = serializers.PrimaryKeyRelatedField(many=True, queryset=Language.objects.all(), required=True, allow_null=False)
    profile_picture = serializers.ImageField(required=False, allow_null=True)
    facebook_url = serializers.URLField(required=False, allow_blank=True, allow_null=True)
    instagram_url = serializers.URLField(required=False, allow_blank=True, allow_null=True)
    tiktok_url = serializers.URLField(required=False, allow_blank=True, allow_null=True)
    linkedin_url = serializers.URLField(required=False, allow_blank=True, allow_null=True)
    youtube_url = serializers.URLField(required=False, allow_blank=True, allow_null=True)
    note = serializers.CharField(max_length=1500, required=False, allow_blank=True, allow_null=True)
    portfolio_images = serializers.ListField(
        child=serializers.ImageField(
            validators=[FileExtensionValidator(allowed_extensions=['jpg', 'png'])],
            max_length=5*1024*1024
        ),
        max_length=10,
        required=False,
        allow_null=True
    )
    average_rating = serializers.FloatField(read_only=True)
    rating_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Master
        fields = [
            'full_name', 'birthday', 'phone_number', 'password', 'password2', 'gender',
            'profession_category', 'profession_service', 'custom_profession', 'experience',
            'cities', 'districts', 'education', 'education_detail', 'languages',
            'profile_picture', 'facebook_url', 'instagram_url', 'tiktok_url',
            'linkedin_url', 'youtube_url', 'note', 'portfolio_images',
            'average_rating', 'rating_count'
        ]

    def validate(self, data):
        if data.get('password') != data.get('password2'):
            raise serializers.ValidationError({"password2": "Şifrələr uyğun deyil."})

        required_fields = ['full_name', 'birthday', 'phone_number', 'gender',
                          'profession_category', 'profession_service', 'cities',
                          'education', 'languages']
        for field in required_fields:
            if not data.get(field):
                raise serializers.ValidationError({field: "Zəhmət olmasa, məlumatları daxil edin."})

        profession_category = data.get('profession_category')
        profession_service = data.get('profession_service')
        custom_profession = data.get('custom_profession')
        if profession_service and profession_category and profession_service.category != profession_category:
            raise serializers.ValidationError({"profession_service": "Seçilmiş ixtisas bu kateqoriyaya aid deyil."})
        
        is_other_service = profession_service and hasattr(profession_service, 'name') and profession_service.name.lower() == 'other'
        if is_other_service:
            if not custom_profession:
                raise serializers.ValidationError({"custom_profession": "'Digər' xidmət seçilibsə, öz peşənizi daxil edin."})
        else:
            if custom_profession:
                raise serializers.ValidationError({"custom_profession": "Xidmət 'Digər' deyilsə, öz peşənizi daxil etməyin."})
            
        districts = data.get('districts', [])
        cities = data.get('cities', [])
        baku = City.objects.filter(name__iexact='baku').first()
        if districts and (not baku or baku not in cities):
            raise serializers.ValidationError({"districts": "Rayonlar yalnız Bakı şəhəri seçildikdə əlavə oluna bilər."})
        if districts and baku:
            for district in districts:
                if not district or district.city != baku:
                    raise serializers.ValidationError({"districts": "Rayonlar yalnız Bakı şəhərinə aid ola bilər."})

        education = data.get('education')
        education_detail = data.get('education_detail')
        if education and hasattr(education, 'name') and education.name != 'none':
            if not education_detail:
                raise serializers.ValidationError({"education_detail": "Zəhmət olmasa, təhsil ixtisasını daxil edin."})
        elif education_detail:
            raise serializers.ValidationError({"education_detail": "Təhsil 'Yoxdur' seçilibsə, ixtisas daxil edilməməlidir."})

        if not data.get('languages'):
            raise serializers.ValidationError({"languages": "Zəhmət olmasa, dil biliklərini daxil edin."})

        return data

    def validate_password(self, value):
        validate_password(value)
        return value

    def validate_portfolio_images(self, value):
        for img in value:
            if img.size > 5 * 1024 * 1024:
                raise serializers.ValidationError("Hər şəkil 5 MB-dan böyük ola bilməz.")
        return value