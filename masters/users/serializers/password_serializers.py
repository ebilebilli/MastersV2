import redis
from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from models.master_model import Master

from masters.masters import settings
from utils.otp import create_otp, send_otp, check_otp_in_redis, delete_otp_in_redis


class PasswordResetRequestSerializer(serializers.Serializer):
    phone_number = serializers.CharField(max_length=13, required=True)

    def validate_phone_number(self, value):
        if not Master.objects.filter(phone_number=value).exists():
            raise serializers.ValidationError({'error': 'Bu telefon nömrəsi ilə istifadəçi tapılmadı.'})
        return value
    
    def save(self):
        phone_number = self.validated_data['phone_number']
        user = Master.objects.get(phone_number=phone_number)
        code = create_otp(phone_number)
        send_otp(phone_number, code)
        return user


class PasswordResetConfirmSerializer(serializers.Serializer):
    phone_number = serializers.CharField(max_length=13, required=True)
    otp_code = serializers.CharField(max_length=6, required=True)
    new_password = serializers.CharField(write_only=True, required=True)
    new_password_two = serializers.CharField(write_only=True, required=True)

    def validate(self, data):
        if not Master.objects.filter(phone_number=data['phone_number']).exists():
            raise serializers.ValidationError({'phone_number': 'Bu telefon nömrəsi ilə istifadəçi tapılmadı.'})

        check_otp_in_redis(data)
        if data['new_password'] != data['new_password_two']:
            raise serializers.ValidationError({'new_password2': 'Şifrələr uyğun deyil.'})

        user = Master.objects.get(phone_number=data['phone_number'])
        validate_password(data['new_password'], user=user)
        return data

    def save(self):
        phone_number = self.validated_data['phone_number']
        new_password = self.validated_data['new_password']
        user = Master.objects.get(phone_number=phone_number)
        user.set_password(new_password)
        user.save()
        delete_otp_in_redis(phone_number)
        return user