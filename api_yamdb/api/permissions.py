from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsAdminOrReadOnly(BasePermission):
    """Права дооступа. Редоктирование доступно только персоналу"""
    message = 'Доступ разрешен только админу'

    def has_permission(self, request, view):
        return request.method in SAFE_METHODS or request.user and request.user.is_staff
