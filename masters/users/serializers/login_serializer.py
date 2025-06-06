from rest_framework import serializers
from users.models import Master
from utils.validators import phone_validator


class LoginSerializer(serializers.Serializer):
    """
    Serializer for handling Master login using phone number and password.
    Validates phone number format and checks password against stored hash.
    """
    phone_number = serializers.CharField(
        required=True,
        validators=[phone_validator],  
        error_messages={'required': 'Zəhmət olmasa, telefon nömrəsini daxil edin.'}
    )
    password = serializers.CharField(
        required=True,
        write_only=True,
        error_messages={'required': 'Zəhmət olmasa, şifrəni daxil edin.'}
    )

    def validate(self, data):
        """
        Validates phone number and password.

        Raises:
            serializers.ValidationError: If phone number is not found,
            password is incorrect, or the user is inactive.

        Returns:
            dict: Validated data with 'user' key added if authentication is successful.
        """
        phone_number = data.get('phone_number')
        password = data.get('password')

       
        master = Master.objects.get(phone_number=phone_number)
        if not master:
            raise serializers.ValidationError({'phone_number': 'Bu telefon nömrəsi ilə istifadəçi tapılmadı.'})

        if not master.check_password(password):
            raise serializers.ValidationError({'password': 'Şifrə yanlışdır.'})
        
        if not master.is_active:
            raise serializers.ValidationError({
                'phone_number': 'Qeydiyyat tamamlanmayıb. Zəhmət olmasa, qeydiyyatı tamamlayın.'})

        data['user'] = master 
        return data