from rest_framework import serializers
from masters.users.models.master_model import Master


class MasterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Master
        fields = '__all__'
   