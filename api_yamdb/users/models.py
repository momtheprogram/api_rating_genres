from django.contrib.auth.models import AbstractUser

from django.db import models

from api.utils import generate_confirmation_code


class Roles(models.TextChoices):
    USER = 'user'
    MODERATOR = 'moderator'
    ADMIN = 'admin'


class User(AbstractUser):
    """ Переопределение пользователя, добавление нужных полей"""
    role = models.CharField(verbose_name='роль', max_length=50, choices=Roles.choices, default=Roles.USER)
    username = models.CharField(max_length=30, unique=True, blank=False, null=False)
    bio = models.TextField(verbose_name='биография', blank=True, null=True)
    email = models.EmailField(max_length=255, unique=True, blank=False, null=False)
    confirmation_code = models.CharField(verbose_name='Код подтверждения', max_length=100, null=True,
                                         default=generate_confirmation_code())

    @property
    def is_admin(self):
        return self.is_staff or self.role == Roles.ADMIN

    @property
    def is_moderator(self):
        return self.role == Roles.MODERATOR
