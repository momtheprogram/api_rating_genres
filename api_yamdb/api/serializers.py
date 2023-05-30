import datetime as dt

from django.db.models import Avg
from rest_framework.serializers import (
    CharField, ModelSerializer, Serializer, SerializerMethodField,
    SlugRelatedField, ValidationError, EmailField, RegexField
)

from reviews.models import Category, Genre, Title, Comment, Review
from users.models import User


class UserSerializer(ModelSerializer):
    """ Сериализатор для юзера."""

    class Meta:
        model = User
        fields = ('username',
                  'email',
                  'first_name',
                  'last_name',
                  'role',
                  'bio')

    def validate_username(self, username):
        if username.lower() == 'me':
            raise ValidationError('You can not use "me"!')
        return username


class SignUpSerializer(Serializer):
    """Сериалайзер для регистрации."""
    username = RegexField(max_length=150, regex=r'^[\w.@+-]+')
    email = EmailField(max_length=254)

    class Meta:
        # model = User
        fields = ("username", "email")

    def validate(self, attrs):
        username = attrs.get('username')
        # todo подумать над валидацией в сериалзаторе
        # email = attrs.get('email')
        # if_user = User.objects.filter(username=username).exclude(email=email)
        # if if_user.exists():
        #     raise ValidationError('Пользователь с таким именем уже существует')
        #
        # if_email = User.objects.filter(email=email).exclude(username=username)
        # if if_email.exists():
        #     raise ValidationError('Почта уже использовалась')
        if username.lower() == 'me':
            raise ValidationError('Нельзя использовать me')
        return attrs

class TokenSerializer(Serializer):
    """Сериалайзер JWT токена."""
    username = CharField(required=True)
    confirmation_code = CharField(required=True)

    class Meta:
        model = User
        fields = ('username', 'confirmation_code')


class ReviewSerializer(ModelSerializer):
    """Сериализатор отзывов."""
    author = SlugRelatedField(
        many=False,
        read_only=True,
        slug_field='username'
    )

    class Meta:
        read_only_fields = ('id', 'title', 'pub_date')
        fields = ('id', 'text', 'author', 'score', 'pub_date')
        model = Review

    def validate(self, attrs):
        is_exist = Review.objects.filter(
            author=self.context['request'].user,
            title=self.context['view'].kwargs.get('title_id')).exists()
        if is_exist and self.context['request'].method == 'POST':
            raise ValidationError(
                'Пользователь уже оставлял отзыв на это произведение')
        return attrs


class CommentSerializer(ModelSerializer):
    """Сериализатор комментариев."""
    author = SlugRelatedField(
        read_only=True,
        slug_field='username'
    )

    class Meta:
        fields = ('id', 'text', 'author', 'pub_date')
        read_only_fields = ('id', 'review', )
        model = Comment


class GenreSerializer(ModelSerializer):
    """Сериализатор жанров"""

    class Meta:
        model = Genre
        fields = ('name', 'slug')


class CategorySerializer(ModelSerializer):
    """Сериализатор категорий."""

    class Meta:
        model = Category
        fields = ('name', 'slug')


class GetTitleSerializer(ModelSerializer):
    """Сериализатор получения произведений"""
    genre = GenreSerializer(many=True)
    category = CategorySerializer()
    rating = SerializerMethodField()

    class Meta:
        model = Title
        fields = '__all__'
        read_only_fields = ('rating', 'category', 'genre')

    def get_rating(self, obj):
        rating = obj.reviews.all().aggregate(Avg('score'))['score__avg']
        if rating:
            return round(rating)
        else:
            return None


class PostTitleSerializer(ModelSerializer):
    """Сериализатор создания произведений"""
    genre = SlugRelatedField(
        slug_field='slug',
        queryset=Genre.objects.all(),
        many=True,
        required=False
    )
    category = SlugRelatedField(
        slug_field='slug',
        queryset=Category.objects.all(),
    )

    class Meta:
        model = Title
        fields = '__all__'

    def validate_year(self, value):
        """Проверяем что произведение не из будущего"""
        if value > dt.date.today().year:
            raise ValidationError(
                'Год выпуска не может быть больше текущего.'
            )
        return value
