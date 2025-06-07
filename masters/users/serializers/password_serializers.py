from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from users.models.master_model import Master
from utils.otp import check_otp_in_redis, delete_otp_in_redis


class PasswordResetRequestSerializer(serializers.Serializer):
    """
    Serializer to handle password reset request via phone number.

    Validates whether a user with the provided phone number exists.
    """
    phone_number = serializers.CharField(max_length=13, required=True)

    def validate_phone_number(self, value):
        """
        Checks if the provided phone number belongs to an existing user.

        Args:
            value (str): The phone number.

        Returns:
            str: The validated phone number.

        Raises:
            serializers.ValidationError: If user does not exist.
        """
        try:
            self._user = Master.objects.get(phone_number=value)
            return value
        except Master.DoesNotExist:
            raise serializers.ValidationError({'error': 'Bu telefon nömrəsi ilə istifadəçi tapılmadı.'})
            
    def save(self):
        """
        Returns the user instance corresponding to the validated phone number.

        Returns:
            Master: The user instance.
        """
        return self._user

class PasswordResetConfirmSerializer(serializers.Serializer):
    """
    Serializer to confirm password reset using OTP and set a new password.

    Validates OTP, ensures new passwords match, and applies Django's 
    password validation policy.
    """
    phone_number = serializers.CharField(max_length=13, required=True)
    otp_code = serializers.CharField(max_length=6, required=True)
    new_password = serializers.CharField(write_only=True, required=True)
    new_password_two = serializers.CharField(write_only=True, required=True)
    
    def validate(self, data):
        """
        Validates the OTP and password fields.

        Returns:
            dict: Validated data.

        Raises:
            serializers.ValidationError: On mismatch or invalid OTP/password.
        """
        if not Master.objects.filter(phone_number=data['phone_number']).exists():
            raise serializers.ValidationError({'phone_number': 'Bu telefon nömrəsi ilə istifadəçi tapılmadı.'})
        try:
            check_otp_in_redis(data)
        except Exception as e:
            raise serializers.ValidationError({'otp_code': f'OTP yoxlaması uğursuz: {str(e)}'})
        if data['new_password'] != data['new_password_two']:
            raise serializers.ValidationError({'new_password': 'Şifrələr uyğun deyil.'})
        user = Master.objects.get(phone_number=data['phone_number'])
        validate_password(data['new_password'], user=user)
        return data
        
    def save(self):
        """
        Sets the new password for the user and deletes the OTP.

        Returns:
            Master: The updated user instance.
        """
        phone_number = self.validated_data['phone_number']
        new_password = self.validated_data['new_password']
        user = Master.objects.get(phone_number=phone_number)
        user.set_password(new_password)
        user.save()
        delete_otp_in_redis(phone_number)
        return user