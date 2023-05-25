from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets

from api.serializers import (
    CategorySerializer,
    GenreSerializer,
    GetTitleSerializer,
    PostTitleSerializer,
)
from reviews.models import Category, Genre, Title
from .utils import BaseViewSet
from .permissions import IsAdminOrReadOnly


class TitleViewSet(viewsets.ModelViewSet):
    """Вьюсет для произведений."""
    queryset = Title.objects.all()
    permission_classes = (IsAdminOrReadOnly,)
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = ('name', 'year', 'genre', 'category',)

    def get_serializer_class(self):
        """Используем сериализатор в зависимости от типа запроса"""
        if self.action in ('POST', 'PUT', 'PATCH'):
            return PostTitleSerializer
        return GetTitleSerializer


class GenreViewSet(BaseViewSet):
    """Вьюсет для жанров"""
    queryset = Genre.objects.all()
    serializer_class = CategorySerializer


class CategoryViewSet(BaseViewSet):
    """Вьюсет для категорий"""
    queryset = Category.objects.all()
    serializer_class = GenreSerializer
