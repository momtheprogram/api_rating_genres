from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsAuthor(BasePermission):
    """
    Редактирование разрешено только Автору.
    """

    def has_object_permission(self, request, view, obj):
        return (request.user.is_authenticated
                and obj.author == request.user)


class IsModerator(BasePermission):
    """
    Редактирование разрешено только Модератору.
    """
    message = 'Доступ разрешен только Модератору'

    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_moderator

    def has_object_permission(self, request, view, obj):
        return request.user.is_authenticated and request.user.is_moderator


class IsAuthorAdminModeratorOrReadOnly(BasePermission):
    def has_permission(self, request, view):
        return request.method in SAFE_METHODS or request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        return (request.method in SAFE_METHODS or request.user.is_authenticated
                and (obj.author == request.user or request.user.is_admin
                     or request.user.is_moderator))


class IsAdmin(BasePermission):
    message = 'Доступ разрешен только Администратору'

    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_admin

    def has_object_permission(self, request, view, obj):
        return request.user.is_authenticated and request.user.is_admin


class IsAdminOrReadOnly(BasePermission):
    """
    Редактирование разрешено только Администратору.
    Чтение разрешено всем.
    """
    message = 'Доступ разрешен только админу'

    def has_permission(self, request, view):
        return (request.method in SAFE_METHODS
                or (request.user.is_authenticated and request.user.is_admin))
