from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator

from django.db import models


class Roles(models.TextChoices):
    USER = 'user'
    MODERATOR = 'moderator'
    ADMIN = 'admin'


class User(AbstractUser):
    """ Переопределение пользователя, добавление нужных полей"""
    role = models.CharField(
        verbose_name='роль',
        max_length=150,
        choices=Roles.choices,
        default=Roles.USER
    )
    username = models.CharField(
        max_length=150,
        unique=True,
        validators=[
            RegexValidator(
                regex=r'^[\w.@+-]+',
                message=r'Username must be like ^[\w.@+-]+ regex'
            ),
        ]
    )
    bio = models.TextField(
        verbose_name='биография',
        blank=True,
        null=True
    )
    email = models.EmailField(
        max_length=254,
        unique=True,
    )
    confirmation_code = models.CharField(
        verbose_name='Код подтверждения',
        max_length=100,
        null=True,
    )
    first_name = models.CharField(
        verbose_name='Имя',
        max_length=150, blank=True,
    )
    last_name = models.CharField(
        verbose_name='Фамилия',
        max_length=150, blank=True,
    )

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return self.username

    @property
    def is_user(self):
        return self.role == Roles.USER

    @property
    def is_admin(self):
        return self.is_superuser or self.role == Roles.ADMIN

    @property
    def is_moderator(self):
        return self.role == Roles.MODERATOR
