from rest_framework import filters, mixins, viewsets
from rest_framework.pagination import PageNumberPagination, LimitOffsetPagination

from .permissions import IsAdminOrReadOnly


class BaseViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    """Базовый вьюсет с ограниченными правами"""
    permission_classes = (IsAdminOrReadOnly,)
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)
    lookup_field = 'slug'
