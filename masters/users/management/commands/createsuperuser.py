from django.contrib.auth.management.commands import createsuperuser
from django.core.management import CommandError
from users.models import Master

class Command(createsuperuser.Command):
    help = 'Create a superuser for the Master model'

    def add_arguments(self, parser):
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
        options.setdefault('phone_number', options.get('username'))
        username = options.get('phone_number')
        full_name = options.get('full_name')

        if username and not full_name:
            raise CommandError("You must specify --full_name when using --phone_number.")

        self.UserModel = Master
        super().handle(*args, **options)

    def get_input_data(self, field, message, default=None):
        if field.name == 'phone_number':
            message = 'Mobil nömrə: '
        elif field.name == 'full_name':
            message = 'Ad və soyad: '
        return super().get_input_data(field, message, default)