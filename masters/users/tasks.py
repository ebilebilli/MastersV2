from celery import shared_task

from utils.otp import create_otp


@shared_task
def send_otp_task(phone_number):
    #In next progress we need to buy sms service for real otp code system
    #This is only for test
    code = create_otp(phone_number)
    return f'Telefon nömrəsi {phone_number} üçün OTP: {code}'