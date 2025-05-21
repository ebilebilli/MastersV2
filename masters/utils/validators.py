from django.core.validators import RegexValidator


phone_validator = RegexValidator(
    regex=r'^(\+994)(50|51|55|70|77|99)[0-9]{7}$',
    message="Mobil nömrə düzgün daxil edilməyib. 50 123 45 67 formatında daxil edin."
)

az_letters_validator = RegexValidator(
    regex=r'^[a-zA-ZəƏöÖüÜşŞçÇğĞıİ\s]+$',
    message='Yalnız Azərbaycan hərfləri ilə yazılmalıdır.'
)