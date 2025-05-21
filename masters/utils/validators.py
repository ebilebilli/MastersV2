from django.core.validators import RegexValidator


phone_validator = RegexValidator(
    regex=r'^(\+994)(50|51|55|70|77|99)[0-9]{7}$',
    message="Mobil nömrə düzgün daxil edilməyib. 50 123 45 67 formatında daxil edin."
)

az_letters_validator = RegexValidator(
    regex=r'^[a-zA-ZəƏöÖüÜşŞçÇğĞıİ\s]+$',
    message='Yalnız Azərbaycan hərfləri ilə yazılmalıdır.'
)

from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import datetime, timedelta

def validate_birthday(value):
    today = timezone.now().date()
    
    if isinstance(value, str):
        try:
            value = datetime.strptime(value, '%Y-%m-%d').date()
        except ValueError:
            raise ValidationError("Tarix formatı düzgün deyil. Format belə olmalıdır: YYYY-MM-DD")
    
    if value > today:
        raise ValidationError("Ad günü gələcək tarix ola bilməz.")

    min_allowed_date = today - timedelta(days=365*100)
    if value < min_allowed_date:
        raise ValidationError("Ad günü 100 ildən daha köhnə ola bilməz.")
