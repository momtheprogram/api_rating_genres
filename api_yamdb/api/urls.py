from rest_framework.routers import DefaultRouter
from django.urls import include, path

from .views import (
    CategoryViewSet, GenreViewSet, TitleViewSet, RegisterView,
    TokenView, UsersViewSet, CommentViewSet, ReviewViewSet
)

app_name = 'api'

router_v1 = DefaultRouter()

router_v1.register(r'users', UsersViewSet, basename='users')
router_v1.register(r'titles', TitleViewSet)
router_v1.register(r'genres', GenreViewSet)
router_v1.register(r'categories', CategoryViewSet)
router_v1.register(
    r'titles/(?P<title_id>[0-9]+)/reviews',
    ReviewViewSet,
    basename='Review'
)
router_v1.register(
    r'titles/(?P<title_id>[0-9]+)/reviews/(?P<review_id>[0-9]+)/comments',
    CommentViewSet,
    basename='Comment'
)
# jwtpatterns = [
#     path('token/', get_jwt_token, name='token_obtain_pair'),
#     path('signup/', sign_up, name='signup'),
# ]

urlpatterns = [
    path('', include(router_v1.urls)),
    path('auth/signup/', RegisterView.as_view(),
         name='get_confirmation_code'),
    path('auth/token/', TokenView.as_view(), name='get_token'),
]
