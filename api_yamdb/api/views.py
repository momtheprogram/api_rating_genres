from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.db import IntegrityError
from django.db.models import Avg
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, status
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet
from rest_framework_simplejwt.tokens import AccessToken

from api_yamdb.settings import EMAIL_HOST_USER
from .filters import TitleFilter
from .permissions import (
    IsAdmin,
    IsAdminOrReadOnly,
    IsAuthorAdminModeratorOrReadOnly,
)
from .serializers import (
    CategorySerializer,
    CommentSerializer,
    GenreSerializer,
    GetTitleSerializer,
    PostTitleSerializer,
    ReviewSerializer,
    SignUpSerializer,
    TokenSerializer,
    UserSerializer,
)
from .utils import CatGenreViewSet
from reviews.models import Category, Genre, Review, Title
from users.models import User


class SignUp(APIView):
    """
    Получает email и username, отправляет
    письмо с confirmation_code на email.
    """
    permission_classes = (AllowAny,)

    def post(self, request):
        serializer = SignUpSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            user, _ = User.objects.get_or_create(
                email=serializer.data['email'],
                username=serializer.data['username']
            )
        except IntegrityError:
            return Response(
                {'username': 'Пользователь с похожим username или email '
                 'уже существует'},
                status=status.HTTP_400_BAD_REQUEST
            )
        confirmation_code = default_token_generator.make_token(user)
        user.confirmation_code = confirmation_code
        user.save()
        send_mail(
            subject='Код подтверждения регистрации',
            message='Вы зарегистрировались в "YAMDB"! '
                    f'Ваш код подтвержения: {confirmation_code}',
            from_email=EMAIL_HOST_USER,
            recipient_list=[user.email],
            fail_silently=False,
        )
        return Response(serializer.data, status=status.HTTP_200_OK)


class TokenView(APIView):
    """
    Получает email и confirmation_code, возвращает токен
    """
    permission_classes = (AllowAny,)

    def post(self, request):
        serializer = TokenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        username = serializer.data['username']
        user = get_object_or_404(User, username=username)
        confirmation_code = serializer.data['confirmation_code']
        if not default_token_generator.check_token(user, confirmation_code):
            return Response(
                {'confirmation_code': 'Неверный код'},
                status=status.HTTP_400_BAD_REQUEST
            )
        token = AccessToken.for_user(user)
        return Response({'token': str(token)}, status=status.HTTP_200_OK)


class UsersViewSet(ModelViewSet):
    """
    Вьюсет для работы с пользователями
    """
    serializer_class = UserSerializer
    queryset = User.objects.all()
    lookup_field = 'username'
    permission_classes = (IsAdmin,)
    filter_backends = (filters.SearchFilter,)
    search_fields = ('username',)
    http_method_names = ('get', 'post', 'delete', 'patch')

    @action(
        detail=False, permission_classes=(IsAuthenticated,),
        methods=['get', 'patch'],
    )
    def me(self, request):
        if request.method == 'GET':
            serializer = self.get_serializer(request.user)
            return Response(serializer.data, status=status.HTTP_200_OK)

        serializer = self.get_serializer(
            request.user, data=request.data, partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save(role=request.user.role, partial=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class TitleViewSet(ModelViewSet):
    """Вьюсет для произведений."""
    queryset = Title.objects.all().annotate(rating=Avg('reviews__score'))
    permission_classes = (IsAdminOrReadOnly,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = TitleFilter

    def get_serializer_class(self):
        """Выбор сериализатора по типу запроса"""
        if self.action in ('list', 'retrieve'):
            return GetTitleSerializer
        return PostTitleSerializer


class GenreViewSet(CatGenreViewSet):
    """Вьюсет для жанров"""
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer


class CategoryViewSet(CatGenreViewSet):
    """Вьюсет для категорий"""
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class CommentViewSet(ModelViewSet):
    serializer_class = CommentSerializer
    permission_classes = [IsAuthorAdminModeratorOrReadOnly]

    def get_queryset(self):
        title_id = self.kwargs.get('title_id')
        review_id = self.kwargs.get('review_id')
        review = get_object_or_404(
            Review, pk=review_id, title_id=title_id,
        )
        return review.comments.all()

    def perform_create(self, serializer):
        title_id = self.kwargs.get('title_id')
        review_id = self.kwargs.get('review_id')
        review = get_object_or_404(
            Review, pk=review_id, title_id=title_id,
        )
        serializer.save(author=self.request.user, review=review)


class ReviewViewSet(ModelViewSet):
    serializer_class = ReviewSerializer
    permission_classes = [IsAuthorAdminModeratorOrReadOnly]

    def get_queryset(self):
        title = get_object_or_404(Title, pk=self.kwargs.get('title_id'))
        return title.reviews.all().order_by('id')

    def perform_create(self, serializer):
        title = get_object_or_404(Title, pk=self.kwargs.get('title_id'))
        serializer.save(author=self.request.user, title=title)
