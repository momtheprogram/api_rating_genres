import random
import string

from django.core.mail import send_mail


def send_mail_to_user(email, confirmation_code):
    send_mail(
        subject='Регистрация',
        message='Регистрация прошла успешно '
                f'Код подтверждения: {confirmation_code}',
        from_email='foryamdb@gmail.com',
        recipient_list=[email],
        fail_silently=False,
    )

def generate_confirmation_code():
    return ''.join(random.choices(string.digits + string.ascii_uppercase,
                                  k=10))
