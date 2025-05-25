from django.contrib.auth.models import BaseUserManager


class MasterUserManager(BaseUserManager):
    def create_user(self, phone_number, full_name, password=None, **extra_fields):
        if not phone_number:
            raise ValueError('Mobil nömrə mütləq daxil edilməlidir.')
        if not full_name:
            raise ValueError('Ad və soyad mütləq daxil edilməlidir.')

        user = self.model(
            phone_number=phone_number,
            full_name=full_name,
            **extra_fields
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, phone_number, full_name, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        extra_fields.setdefault('is_active_on_main_page', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser üçün is_staff=True olmalıdır.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser üçün is_superuser=True olmalıdır.')

        return self.create_user(phone_number, full_name, password, **extra_fields)    