# import random
# import string
from django.conf import settings
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from rest_framework import filters, mixins, viewsets

from .permissions import IsAdminOrReadOnly


def send_confirmation_code(user):
    confirmation_code = default_token_generator.make_token(user)
    subject = 'Код подтверждения YaMDb'
    message = f'{confirmation_code} - ваш код для авторизации на YaMDb'
    admin_email = settings.ADMIN_EMAIL
    user_email = [user.email]
    return send_mail(subject, message, admin_email, user_email)
# def send_mail_to_user(email, confirmation_code):
#     send_mail(
#         subject='Регистрация',
#         message='Регистрация прошла успешно '
#                 f'Код подтверждения: {confirmation_code}',
#         from_email='foryamdb@gmail.com',
#         recipient_list=[email],
#         fail_silently=False,
#     )
#
#
# def generate_confirmation_code():
#     return ''.join(random.choices(string.digits + string.ascii_uppercase,
#                                   k=10))


class BaseViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    """Базовый вьюсет с ограниченными правами"""
    permission_classes = (IsAdminOrReadOnly,)
    filter_backends = (filters.SearchFilter)
    search_fields = ('name',)
