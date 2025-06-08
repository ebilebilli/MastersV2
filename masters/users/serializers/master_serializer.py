from rest_framework import serializers
from users.models.master_model import CustomerUser


class MasterSerializer(serializers.ModelSerializer):

    class Meta:
        model = CustomerUser
        exclude = [
            'password', 'is_superuser', 'is_staff', 'user_permissions', 'groups',
            'last_login', 'date_joined', 'is_active', 
        ]
   