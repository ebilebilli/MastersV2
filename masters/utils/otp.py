import redis
from django.core.exceptions import ValidationError
from django.conf import settings
from random import choices


def create_otp(phone_number):
    """
    Generates a One-Time Password (OTP) code and stores it in Redis
    with a 3-minute expiration time for the given phone number.

    Args:
        phone_number (str): The phone number to associate the OTP with.

    Returns:
        str: The generated OTP code.
    """
    #code = ''.join(choices('0123456789', k=6))
    code = 111111   #it is default code for development

    redis_client = redis.Redis(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            db=settings.REDIS_DB
        )
    redis_key = f'otp:{phone_number}'
    redis_client.setex(redis_key, 180, code)

    return code


def check_otp_in_redis(data):
    """
    Checks if the OTP code provided in `data` matches the stored OTP 
    in Redis for the given phone number.

    Args:
        data (dict): A dictionary containing 'phone_number' and 'otp_code' keys.

    Raises:
        ValidationError: If the OTP is missing, expired, or does not match.
    """
    redis_client = redis.Redis(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            db=settings.REDIS_DB
        )
    redis_key = f"otp:{data['phone_number']}"
    stored_code = redis_client.get(redis_key)

    if not stored_code or stored_code.decode('utf-8') != data['otp_code']:
        raise ValidationError({'otp_code': 'Yanlış və ya vaxtı keçmiş OTP kodu.'})


def delete_otp_in_redis(phone_number):
    """
    Deletes the OTP code stored in Redis for the given phone number.

    Args:
        phone_number (str): The phone number whose OTP entry should be deleted.
    """
    redis_client = redis.Redis(
        host=settings.REDIS_HOST,
        port=settings.REDIS_PORT,
        db=settings.REDIS_DB
        )
    redis_client.delete(f'otp:{phone_number}')
