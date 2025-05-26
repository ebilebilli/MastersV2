from rest_framework import serializers
from users.models import Master
from core.models.city_model import City


class MasterSerializer(serializers.ModelSerializer):
    cities = serializers.StringRelatedField(many=True)
    districts = serializers.StringRelatedField(many=True)
    profession_category = serializers.StringRelatedField()
    profession_service = serializers.StringRelatedField()
    languages = serializers.StringRelatedField(many=True)
    average_rating = serializers.FloatField(read_only=True)
    rating_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Master
        fields = [
            'full_name', 'birthday', 'phone_number', 'gender',
            'profession_category', 'profession_service', 'custom_profession',
            'experience', 'cities', 'districts', 'education', 'education_detail', 'languages',
            'average_rating', 'rating_count' 
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
        cities = data.get('cities', [])
        baku = City.objects.filter(name__iexact='baku').first()
        if districts and (not baku or baku not in cities):
            raise serializers.ValidationError({"districts": "Rayonlar yalnız Bakı şəhəri seçildikdə əlavə oluna bilər."})

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