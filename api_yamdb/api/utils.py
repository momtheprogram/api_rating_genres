from rest_framework import filters, mixins, viewsets

from .permissions import IsAdminOrReadOnly


MAX_TITLE_LENGTH = 200
MAX_STR_TEXT_LIMIT = 15


class CatGenreViewSet(
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
