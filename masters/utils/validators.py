import re
from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import datetime, timedelta


phone_validator = RegexValidator(
    regex=r'^(50|51|55|70|77|99)[0-9]{7}$',
    message="Mobil nömrə düzgün daxil edilməyib. 50 123 45 67 formatında daxil edin."
)

az_letters_validator = RegexValidator(
    regex=r'^[a-zA-ZəƏöÖüÜşŞçÇğĞıİ\s]+$',
    message='Yalnız Azərbaycan hərfləri ilə yazılmalıdır.'
)


def validate_birthday(value):
    today = timezone.now().date()
    
    if isinstance(value, str):
        try:
            value = datetime.strptime(value, '%d-%m-%Y').date()
        except ValueError:
            raise ValidationError("Tarix formatı düzgün deyil. Format belə olmalıdır: DD-MM-YYYY")
    
    if value > today:
        raise ValidationError("Doğum günü gələcək tarix ola bilməz.")

    min_allowed_date = today - timedelta(days=365*100)
    if value < min_allowed_date:
        raise ValidationError("Doğum günü 100 ildən daha köhnə ola bilməz.")


class CustomPasswordValidator:
    def validate(self, password, user=None):
        if not password:
            raise ValidationError("Şifrə məcburi xanadır.")

        if not re.search(r'[A-Za-z]', password):
            raise ValidationError("Şifrə hərflər içerməlidir.")
        if not re.search(r'\d', password):
            raise ValidationError("Şifrə rəqəmlər içerməlidir.")
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            raise ValidationError("Şifrə simvollardan (məsələn !, @, #) ibarət olmalıdır.")

    def get_help_text(self):
        return "Peşə sahibi şifrəsini daxil edir. Şifrə hərf, rəqəm və simvoldan ibarət olmalıdır."
