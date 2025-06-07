from django.contrib.auth.models import BaseUserManager


class MasterUserManager(BaseUserManager):
    """
    Custom user manager for the Master model using phone number as the unique identifier.
    """
    def create_user(self, phone_number, full_name, password=None, **extra_fields):
        """
        Creates and saves a regular Master user with the given phone number, full name, and optional password.

        Args:
            phone_number (str): User's phone number. Must be provided.
            full_name (str): User's full name. Must be provided.
            password (str, optional): User's password. Defaults to None.
            **extra_fields: Any additional fields for the user model.

        Raises:
            ValueError: If phone_number or full_name is not provided.

        Returns:
            Master: The created Master user instance.
        """
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
        """
        Creates and saves a superuser (admin) with the given phone number, full name, and password.

        Ensures that is_staff, is_superuser, is_active, and is_active_on_main_page
        are set to True.

        Args:
            phone_number (str): Superuser's phone number.
            full_name (str): Superuser's full name.
            password (str, optional): Password for the superuser. Defaults to None.
            **extra_fields: Any additional fields.

        Raises:
            ValueError: If is_staff or is_superuser is not True.

        Returns:
            Master: The created superuser instance.
        """
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        extra_fields.setdefault('is_active_on_main_page', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser üçün is_staff=True olmalıdır.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser üçün is_superuser=True olmalıdır.')

        return self.create_user(phone_number, full_name, password, **extra_fields)    