from rest_framework.routers import DefaultRouter
from django.urls import include, path

from .views import CategoryViewSet, GenreViewSet, TitleViewSet, RegisterView, TokenView, UsersViewSet


router_v1 = DefaultRouter()
router_v1.register(r'users', UsersViewSet, basename='users')
router_v1.register(r'titles', TitleViewSet)
router_v1.register(r'genres', GenreViewSet)
router_v1.register(r'categories', CategoryViewSet)

urlpatterns = [
    path('', include(router_v1.urls)),
    path('auth/email/', RegisterView.as_view(),
         name='get_confirmation_code'),
    path('auth/token/', TokenView.as_view(), name='get_token'),
]
