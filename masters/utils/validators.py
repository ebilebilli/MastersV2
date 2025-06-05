import re
from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import datetime, timedelta


phone_validator = RegexValidator(
    regex=r'^(50|51|55|70|77|99)[0-9]{7}$',
    message="Mobil nömrə düzgün daxil edilməyib. 50 123 45 67 formatında daxil edin."
)

az_letters_name_validator = RegexValidator(
    regex=r'^[a-zA-ZəƏöÖüÜşŞçÇğĞıİ\s]+$',
    message='Yalnız Azərbaycan hərfləri ilə yazılmalıdır.'
)

az_letters_validator = RegexValidator(
    regex=r'^[a-zA-ZəƏöÖüÜşŞçÇğĞıİ\s.,!?-]+$',
    message='Yalnız Azərbaycan hərfləri ilə yazılmalıdır.'
)

def validate_full_name(value):
    az_letters_name_validator(value)

    if len(value.strip()) < 7:
        raise ValidationError('Ad və soyad cəmi ən azı 7 simvol olmalıdır.')

    if ' ' not in value.strip():
        raise ValidationError('Ad və soyad arasında boşluq olmalıdır.')

    if value.strip() == '' or value.strip().count(' ') > value.strip().count('') - 1:
        raise ValidationError('Düzgün ad və soyad daxil edin.')

    return value


def validate_birthday(value):
    today = timezone.now().date()
    min_allowed_date = today - timedelta(days=365*100)
    min_allowed_age = today - timedelta(days=365 * 13)
    
    if isinstance(value, str):
        try:
            value = datetime.strptime(value, '%d-%m-%Y').date()
        except ValueError:
            raise ValidationError("Tarix formatı düzgün deyil. Format belə olmalıdır: DD-MM-YYYY")
    
    if value > today:
        raise ValidationError("Doğum günü gələcək tarix ola bilməz.")
    
    if value > min_allowed_age:
        raise ValidationError("Istifadəçin yaşı 13 dən aşağı ola bilməz")
    
    if value < min_allowed_date:
        raise ValidationError("Doğum günü 100 ildən daha köhnə ola bilməz.")
    
    
def not_only_whitespace(value):
    if not value.strip():
        raise ValidationError("Boşluqdan ibarət şərh göndərilə bilməz.")
    
    if len(value.strip()) < 3:
        raise ValidationError("Mətn ən azı 3 simvol olmalıdır.")


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


class SocialURLValidator:
    @staticmethod
    def facebook(value):
        if value and not (value.startswith('https://facebook.com/') or value.startswith('https://www.facebook.com/')):
            raise ValidationError("Facebook URL düzgün formatda deyil.")
    
    @staticmethod
    def instagram(value):
        if value and not (value.startswith('https://instagram.com/') or value.startswith('https://www.instagram.com/')):
            raise ValidationError("Instagram URL düzgün formatda deyil.")
    
    @staticmethod
    def tiktok(value):
        if value and not (value.startswith('https://tiktok.com/') or value.startswith('https://www.tiktok.com/')):
            raise ValidationError("TikTok URL düzgün formatda deyil.")
    
    @staticmethod
    def linkedin(value):
        if value and not (value.startswith('https://linkedin.com/') or value.startswith('https://www.linkedin.com/')):
            raise ValidationError("LinkedIn URL düzgün formatda deyil.")
    
    @staticmethod
    def youtube(value):
        if value and not (value.startswith('https://youtube.com/') or 
                          value.startswith('https://www.youtube.com/') or 
                          value.startswith('https://youtu.be/')):
            raise ValidationError("YouTube URL düzgün formatda deyil.")