from rest_framework import serializers

from users.models.customeruser_model import Master
from services.models.category_model import Category
from services.models.service_model import ServiceTemplate
from core.models.city_model import City, District

class CitySerializer(serializers.ModelSerializer):
    class Meta:
        model = City
        fields = ['id', 'name', 'display_name']

class DistrictSerializer(serializers.ModelSerializer):
    class Meta:
        model = District
        fields = ['id', 'name', 'display_name', 'city']

class MasterSerializer(serializers.ModelSerializer):
    cities = serializers.PrimaryKeyRelatedField(many=True, queryset=City.objects.all())
    districts = serializers.PrimaryKeyRelatedField(many=True, queryset=District.objects.all(), required=False)
    profession_category = serializers.PrimaryKeyRelatedField(queryset=Category.objects.all())
    profession_service = serializers.PrimaryKeyRelatedField(queryset=ServiceTemplate.objects.all())

    class Meta:
        model = Master
        fields = [
            'full_name', 'birthday', 'phone_number', 'gender',
            'profession_category', 'profession_service', 'custom_profession',
            'experience', 'cities', 'districts', 'education', 'education_specialization'
        ]

    def validate(self, data):
        # Məcburi sahələr
        required_fields = ['profession_category', 'profession_service', 'cities']
        for field in required_fields:
            if not data.get(field):
                raise serializers.ValidationError({field: "Zəhmət olmasa, məlumatları daxil edin."})

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
        user = Master.objects.create_user(**validated_data)
        user.cities.set(cities)
        user.districts.set(districts)
        return user