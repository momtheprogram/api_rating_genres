from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    CategoryViewSet, GenreViewSet, TitleViewSet, SignUp,
    TokenView, UsersViewSet, CommentViewSet, ReviewViewSet
)

app_name = 'api'

router_v1 = DefaultRouter()

router_v1.register(r'users', UsersViewSet, basename='users')
router_v1.register(r'titles', TitleViewSet)
router_v1.register(r'genres', GenreViewSet)
router_v1.register(r'categories', CategoryViewSet)
router_v1.register(
    r'titles/(?P<title_id>\d+)/reviews',
    ReviewViewSet,
    basename='review'
)
router_v1.register(
    r'titles/(?P<title_id>\d+)/reviews/(?P<review_id>\d+)/comments',
    CommentViewSet,
    basename='comment'
)

urlpatterns = [
    path('', include(router_v1.urls)),
    path('auth/signup/', SignUp.as_view(),
         name='signup'),
    path('auth/token/', TokenView.as_view(), name='get_token'),
]
