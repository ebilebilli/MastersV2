from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from django.core.validators import FileExtensionValidator
from users.models import Master
from core.models.city_model import City, District
from core.models.education_model import Education
from core.models.language_model import Language


class PersonalInformationSerializer(serializers.ModelSerializer):
    password2 = serializers.CharField(write_only=True, required=True, label="Şifrəni təkrar yazın")
    class Meta:
        model = Master
        fields = ['full_name', 'birthday', 'phone_number', 'password', 'password2', 'gender']
    
    def validate(self, data):
        if data['password'] != data['password2']:
            raise serializers.ValidationError({"password2": "Şifrələr uyğun deyil."})
        return data
    
    def validate_password(self, value):
        validate_password(value)  
        return value
    
    
class ProfessionInformationSerializer(serializers.ModelSerializer):
    cities = serializers.PrimaryKeyRelatedField(many=True, queryset=City.objects.all(), required=True)
    districts = serializers.PrimaryKeyRelatedField(many=True, queryset=District.objects.all(), required=False,)
    
    class Meta:
        model = Master
        fields = ['profession_category', 'profession_service', 'experience', 'cities', 'districts']
        
    def validate(self, data):
        required_fields = ['profession_category', 'profession_service', 'cities']
        for field in required_fields:
            if not data.get(field):
                raise serializers.ValidationError({field: "Zəhmət olmasa, məlumatları daxil edin."})

        profession = data.get('profession_service')
        profession_category = data.get('profession_category')

        if profession and profession_category and profession.category != profession_category:
            raise serializers.ValidationError({"profession_service": "Seçilmiş ixtisas bu kateqoriyaya aid deyil."})
        
        districts = data.get('districts', [])
        cities = data.get('cities', [])
        baku = City.objects.filter(name__iexact='baku').first()
        if districts and (not baku or baku not in cities):
            raise serializers.ValidationError({"districts": "Rayonlar yalnız Bakı şəhəri seçildikdə əlavə oluna bilər."})
        
        return data


class AdditionalInformationSerializer(serializers.ModelSerializer):
    languages = serializers.PrimaryKeyRelatedField(many=True, queryset=Language.objects.all(), required=True)
    portfolio_images = serializers.ListField(
        child=serializers.ImageField(
            validators=[FileExtensionValidator(allowed_extensions=['jpg', 'png'])],
            max_length=5*1024*1024  
        ),
        max_length=10,
        required=False
    )
    average_rating = serializers.FloatField(read_only=True)
    rating_count = serializers.IntegerField(read_only=True)
    class Meta:
        model = Master
        fields = [
            'education', 'education_detail', 'languages', 'profile_picture',
            'facebook_url', 'instagram_url', 'tiktok_url', 'linkedin_url', 'youtube_url',
            'note', 'portfolio_images', 'average_rating', 'rating_count'
        ]
    
    def validate(self, data):
        if not data.get('languages'):
            raise serializers.ValidationError({"languages": "Zəhmət olmasa, dil biliklərini daxil edin."})

        education = data.get('education')
        education_detail = data.get('education_detail')
        if education and education.name != 'none':
            if not education_detail:
                raise serializers.ValidationError({"education_detail": "Zəhmət olmasa, təhsil ixtisasını daxil edin."})
        else:
            if education_detail:
                raise serializers.ValidationError({"education_detail": "Təhsil 'Yoxdur' seçilibsə, ixtisas daxil edilməməlidir."})
        return data

    def validate_portfolio_images(self, value):
        for img in value:
            if img.size > 5 * 1024 * 1024:  
                raise serializers.ValidationError("Hər şəkil 5 MB-dan böyük ola bilməz.")
        return value