from rest_framework import viewsets

from api.serializers import (
    CategorySerializer,
    GenreSerializer,
    TitleSerializer,
)
from reviews.models import Title, Genre, Category
from .utils import BaseViewSet
from .permissions import IsAdminOrReadOnly


class TitleViewSet(viewsets.ModelViewSet):
    queryset = Title.objects.all()
    serializer_class = TitleSerializer
    permission_classes = (IsAdminOrReadOnly,)


class GenreViewSet(BaseViewSet):
    queryset = Genre.objects.all()
    serializer_class = CategorySerializer


class CategoryViewSet(BaseViewSet):
    queryset = Category.objects.all()
    serializer_class = GenreSerializer
