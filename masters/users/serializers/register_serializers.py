from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from django.core.validators import FileExtensionValidator

from users.models import Master
from users.models.master_work_img_model import MasterWorkImage
from core.models.city_model import City, District
from core.models.language_model import Language


__all__ = [
    'UserRoleSelectionSerializer',
    'PersonalInformationSerializer',
    'AdditionalInformationSerializer',
    'CustomerRegistrationSerializer'
]

class UserRoleSelectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Master
        fields = ['user_role']


class PersonalInformationSerializer(serializers.ModelSerializer):
    """
    Serializer for collecting personal information during registration.

    Fields include:
    - full name
    - birthday
    - phone number
    - password and password confirmation
    - gender
    """
    password2 = serializers.CharField(write_only=True, required=True, label="Şifrəni təkrar yazın")
    class Meta:
        model = Master
        fields = ['full_name', 'birthday', 'phone_number', 'password', 'password2', 'gender']
    
    def validate(self, data):
        """
        Ensure both password fields match.
        """
        if data['password'] != data['password2']:
            raise serializers.ValidationError({"password2": "Şifrələr uyğun deyil."})
        return data
    
    def validate_password(self, value):
        """
        Apply Django's default password validation.
        """
        validate_password(value)  
        return value
    
    
class ProfessionInformationSerializer(serializers.ModelSerializer):
    """
    Serializer for professional information during master registration.

    Includes fields:
    - profession category and service
    - experience
    - cities and optionally districts
    - custom profession if 'Other' selected
    """
    
    cities = serializers.PrimaryKeyRelatedField(many=True, queryset=City.objects.all(), required=True)
    districts = serializers.PrimaryKeyRelatedField(many=True, queryset=District.objects.all(), required=False,)
    
    class Meta:
        model = Master
        fields = ['profession_category', 'profession_service', 'experience', 'cities', 'districts','custom_profession']
        
    def validate(self, data):
        """
        Performs:
        - Required field check
        - Service-category match validation
        - If 'Other' service selected, `custom_profession` is required
        - Districts allowed only if Baku is selected
        """
        required_fields = ['profession_category', 'profession_service', 'cities']
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
        
        return data


class AdditionalInformationSerializer(serializers.ModelSerializer):
    """
    Serializer for collecting additional profile information.

    Includes:
    - education, education_detail
    - known languages
    - profile picture and social links
    - portfolio image uploads
    - average rating info (read-only)
    """
    
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
        """
        - Ensures at least one language is selected
        - Validates education detail requirement logic
        """
        if not data.get('languages'):
            raise serializers.ValidationError({"languages": "Zəhmət olmasa, dil biliklərini daxil edin."})

        education = data.get('education')
        education_detail = data.get('education_detail')
        if education and hasattr(education, 'name') and education.name != 'none':
            if not education_detail:
                raise serializers.ValidationError({"education_detail": "Zəhmət olmasa, təhsil ixtisasını daxil edin."})
        
        elif education_detail:
            raise serializers.ValidationError({"education_detail": "Təhsil 'Yoxdur' seçilibsə, ixtisas daxil edilməməlidir."})

        return data

    def validate_portfolio_images(self, value):
        """
        Validates uploaded image size and count.
        """
        for img in value:
            if img.size > 5 * 1024 * 1024:  
                raise serializers.ValidationError("Hər şəkil 5 MB-dan böyük ola bilməz.")
            
        if len(value) > 10:
            raise serializers.ValidationError("Maksimum 10 şəkil yükləyə bilərsiniz")
        
        return value
    
    def create(self, validated_data):
        """
        Handles saving portfolio images along with master profile creation.
        """
        master_work_images = validated_data.pop('master_work_images', [])
        master = Master.objects.create(**validated_data)
        for img in master_work_images:
            MasterWorkImage.objects.create(master=master, image=img)
        return master


class CustomerRegistrationSerializer(serializers.ModelSerializer):
    password2 = serializers.CharField(write_only=True, required=True, label="Şifrəni təkrar yazın")
    class Meta:
        model = Master
        fields = ['full_name', 'birthday', 'phone_number', 'password', 'password2', 'gender']
    
    def validate(self, data):
        """
        Ensure both password fields match.
        """
        if data['password'] != data['password2']:
            raise serializers.ValidationError({"password2": "Şifrələr uyğun deyil."})
        return data
    
    def validate_password(self, value):
        """
        Apply Django's default password validation.
        """
        validate_password(value)  
        return value