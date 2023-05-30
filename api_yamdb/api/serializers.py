import datetime as dt

from rest_framework.serializers import (
    CharField, EmailField, ModelSerializer, Serializer, SerializerMethodField,
    SlugRelatedField, ValidationError, StringRelatedField,
)
from rest_framework.validators import UniqueValidator

from django.db.models import Avg

from reviews.models import Category, Genre, Title, Comment, Review
from users.models import User, Roles


# class UserSerializer(ModelSerializer):
#     """
#     Сериализатор для юзера
#     """
#     role = CharField(default=Roles.USER, max_length=150,)
#
#     class Meta:
#         model = User
#         fields = ('first_name', 'last_name', 'username',
#                   'bio', 'email', 'role', 'confirmation_code')
#         extra_kwargs = {'confirmation_code': {'write_only': True},
#                         'username': {'required': True},
#                         'email': {'required': True}}

class UserSerializer(ModelSerializer):
    """ Сериализатор для юзера."""
    username = CharField(validators=[UniqueValidator(
        queryset=User.objects.all())],
        required=True,
    )
    email = EmailField(validators=[UniqueValidator(
        queryset=User.objects.all())],
        required=True,
    )
    role = StringRelatedField(read_only=True)

    class Meta:
        model = User
        fields = ('username',
                  'email',
                  'first_name',
                  'last_name',
                  'role',
                  'bio'
                  )

    def validate_username(self, username):
        if username == 'me':
            raise ValidationError('You can not use "me"!')
        return username


class CreateUserSerializer(ModelSerializer):
    """Сериалайзер для создания юзера."""

    class Meta:
        model = User
        fields = ('username',
                  'email',
                  'first_name',
                  'last_name',
                  'role',
                  'bio'
                  )
        read_only_fields = ('role',)


class SignUpSerializer(ModelSerializer):
    """Сериалайзер для регистрации."""
    # username = CharField(
    #     validators=[UniqueValidator(queryset=User.objects.all())]
    # )
    # email = EmailField(
    #     validators=[UniqueValidator(queryset=User.objects.all())]
    # )

    def validate_exist(self, attrs):
        username = attrs.get('username')
        if_user = User.objects.filter(username=username)
        if if_user.exists():
            raise ValidationError('Пользователь с таким именем уже существует')
        email = attrs.get('email')
        if_email = User.objects.filter(email=email)
        if if_email.exists():
            raise ValidationError('Почта уже использовалась')

    def validate_username(self, username):
        if username == 'me':
            raise ValidationError('Нельзя использовать me')
        return username

    class Meta:
        model = User
        fields = ("username", "email")


class TokenSerializer(Serializer):
    """Сериалайзер JWT токена."""
    username = CharField(required=True)
    confirmation_code = CharField(required=True)

    class Meta:
        model = User
        fields = ('username', 'confirmation_code')


class ReviewSerializer(ModelSerializer):
    """
    Сериализатор отзывов
    """
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
    """
    Сериализатор комментариев
    """
    author = SlugRelatedField(
        many=False,
        read_only=True,
        slug_field='username'
    )

    class Meta:
        read_only_fields = ('id', 'review', 'pub_date')
        fields = ('id', 'text', 'author', 'pub_date')
        model = Comment


class GenreSerializer(ModelSerializer):
    """Сериализатор жанров"""
    class Meta:
        model = Genre
        fields = '__all__'


class CategorySerializer(ModelSerializer):
    """Сериализатор категорий."""
    class Meta:
        model = Category
        fields = '__all__'


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
    description = CharField(required=False)
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
        fields = ('__all__')

    def validate_year(self, value):
        """Проверяем что произведение не из будущего"""
        if value > dt.date.today().year:
            raise ValidationError(
                'Год выпуска не может быть больше текущего.'
            )
        return value
