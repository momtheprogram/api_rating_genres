from rest_framework.routers import DefaultRouter

from django.urls import include, path

from .views import CategoryViewSet, GenreViewSet, TitleViewSet

router = DefaultRouter()
router.register(r'titles', TitleViewSet)
router.register(r'genre', GenreViewSet)
router.register(r'category', CategoryViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
