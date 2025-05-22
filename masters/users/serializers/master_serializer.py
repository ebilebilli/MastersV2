from rest_framework import serializers
from masters.users.models import Master
from services.models.category_model import Category
from services.models.service_model import ServiceTemplate
from core.models.city_model import City, District
from core.models.language_model import Language


class MasterSerializer(serializers.ModelSerializer):
    cities = serializers.StringRelatedField(many=True)
    districts = serializers.StringRelatedField(many=True)
    profession_category = serializers.StringRelatedField()
    profession_service = serializers.StringRelatedField()
    languages = serializers.StringRelatedField(many=True)
    average_rating = serializers.FloatField(source='average_rating', read_only=True)
    rating_count = serializers.IntegerField(source='rating_count', read_only=True)

    class Meta:
        model = Master
        fields = [
            'full_name', 'birthday', 'phone_number', 'gender',
            'profession_category', 'profession_service', 'custom_profession',
            'experience', 'cities', 'districts', 'education', 'education_detail', 'languages'
        ]

    def validate(self, data):
        # Mövcud validasiyalar
        required_fields = ['profession_category', 'profession_service', 'cities']
        for field in required_fields:
            if not data.get(field):
                raise serializers.ValidationError({field: "Zəhmət olmasa, məlumatları daxil edin."})

        # Dil bilikləri sahəsinin məcburi olduğunu yoxlama
        if not data.get('languages'):
            raise serializers.ValidationError({"languages": "Zəhmət olmasa, dil biliklərini daxil edin."})

        # Rayonların Bakıya aid olması
        districts = data.get('districts', [])
        baku = City.objects.filter(name='baku').first()
        if districts and baku:
            for district in districts:
                if district.city != baku:
                    raise serializers.ValidationError({"districts": "Rayonlar yalnız Bakı şəhərinə aid ola bilər."})

        # Peşə ixtisasının kateqoriyaya uyğunluğu
        profession = data.get('profession_service')
        profession_category = data.get('profession_category')
        if profession and profession_category and profession.category != profession_category:
            raise serializers.ValidationError({"profession_service": "Seçilmiş ixtisas bu kateqoriyaya aid deyil."})

        # Təhsil və təhsil ixtisası yoxlaması
        education = data.get('education')
        education_detail = data.get('education_detail')
        if education and education.name != 'none':
            if not education_detail:
                raise serializers.ValidationError({"education_detail": "Zəhmət olmasa, təhsil ixtisasını daxil edin."})
        else:
            if education_detail:
                raise serializers.ValidationError({"education_detail": "Təhsil 'Yoxdur' seçilibsə, ixtisas daxil edilməməlidir."})

        return data

    def create(self, validated_data):
        cities = validated_data.pop('cities', [])
        districts = validated_data.pop('districts', [])
        languages = validated_data.pop('languages', [])
        user = Master.objects.create_user(**validated_data)
        user.cities.set(cities)
        user.districts.set(districts)
        user.languages.set(languages)
        return user