from django.contrib import admin

from .models import User


class UserAdmin(admin.ModelAdmin):
    """
    Администрирование ролей пользователей.
    """
    list_display = ("role",)


admin.site.register(User, UserAdmin)
