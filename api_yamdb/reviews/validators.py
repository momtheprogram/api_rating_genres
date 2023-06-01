import datetime as dt

from django.core.exceptions import ValidationError


def validate_year(value):
    """Проверяем что произведение не из будущего"""
    if value > dt.date.today().year:
        raise ValidationError(
            'Год выпуска не может быть больше текущего.'
        )
    return value
