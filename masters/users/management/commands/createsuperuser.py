from django.contrib.auth.management.commands import createsuperuser
from django.core.management import CommandError
from users.models import CustomerUser

class Command(createsuperuser.Command):
    """
    Custom Django management command to create a superuser using the custom CustomerUser model.

    This command overrides the default `createsuperuser` to support additional fields:
    - `phone_number` (used instead of `username`)
    - `full_name` (required for CustomerUser model)

    Usage:
        python manage.py createsuperuser --phone_number=+994501234567 --full_name="Test User"

    Notes:
    - The `phone_number` replaces the default `username` field.
    - The `full_name` argument is required when using this command.
    """
    
    help = 'Create a superuser for the CustomerUser model'

    def add_arguments(self, parser):
        """
        Extend the default createsuperuser arguments by adding:
        - `--phone_number`: Required phone number for the superuser.
        - `--full_name`: Full name of the superuser.
        """
        
        super().add_arguments(parser)
        parser.add_argument(
            '--phone_number', dest='phone_number', default=None,
            help='Specifies the phone number for the superuser.',
        )
        parser.add_argument(
            '--full_name', dest='full_name', default=None,
            help='Specifies the full name for the superuser.',
        )

    def handle(self, *args, **options):
        """
        Sets the phone number as username and checks for required full_name.
        Then delegates to the base createsuperuser handler.
        """
        
        options.setdefault('phone_number', options.get('username'))
        username = options.get('phone_number')
        full_name = options.get('full_name')

        if username and not full_name:
            raise CommandError("You must specify --full_name when using --phone_number.")

        self.UserModel = CustomerUser
        super().handle(*args, **options)

    def get_input_data(self, field, message, default=None):
        """
        Customize prompts for interactive mode (when fields are not passed via CLI).
        """
        
        if field.name == 'phone_number':
            message = 'Mobil nömrə: '
        elif field.name == 'full_name':
            message = 'Ad və soyad: '
        return super().get_input_data(field, message, default)