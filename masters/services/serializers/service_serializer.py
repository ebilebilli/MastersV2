from rest_framework import serializers

from services.models.service_model import Service
from services.models.category_model import Category


class ServiceSerializer(serializers.ModelSerializer):
    category = serializers.SlugRelatedField(
    queryset=Category.objects.all(),
    slug_field='name'
    )
    
    class Meta:
        model = Service
        fields = '__all__'

    def validate_category(self, value):
        if value is None:
            raise serializers.ValidationError("Kateqoriya daxil edilməlidir")
        return value
            
    def validate(self, data):
        user = self.context['request'].user if 'request' in self.context else None
        if user and user.is_authenticated and not self.instance:
            if not self.instance:
                name = data.get('name', '')
                if len(name) > 25 or len(name) < 4:
                    raise serializers.ValidationError("Custom xidmət uzunluğun maksimum 25, minimum isə 4 olmalıdır.")

                display_name = data.get('display_name', '')
                if display_name != name:
                    raise serializers.ValidationError("Custom xidmətin görünən adı xidməti adı ilə eyni olmalıdır.")

                data['owner'] = user
            else:
                if self.instance.owner and self.instance.owner != user:
                    raise serializers.ValidationError('Bu xidməti redaktə etmək icazəniz yoxdur.')
        return data
