import datetime as dt

from rest_framework import serializers
from django.db.models import Avg

from reviews.models import Category, Genre, Title
from users.models import User, Roles


class UserSerializer(serializers.ModelSerializer):
    """
    Сериализатор для юзера
    """
    role = serializers.CharField(default=Roles.USER)

    class Meta:
        fields = ('first_name', 'last_name', 'username',
                  'bio', 'email', 'role', 'confirmation_code')
        model = User
        extra_kwargs = {'confirmation_code': {'write_only': True},
                        'username': {'required': True},
                        'email': {'required': True}}


class GenreSerializer(serializers.ModelSerializer):
    """Сериализатор жанров"""
    class Meta:
        model = Genre
        fields = '__all__'


class CategorySerializer(serializers.ModelSerializer):
    """Сериализатор категорий."""
    class Meta:
        model = Category
        fields = '__all__'


class GetTitleSerializer(serializers.ModelSerializer):
    """Сериализатор получения произведений"""
    genre = GenreSerializer(many=True)
    category = CategorySerializer()
    rating = serializers.SerializerMethodField()

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


class PostTitleSerializer(serializers.ModelSerializer):
    """Сериализатор создания произведений"""
    description = serializers.CharField(required=False)
    genre = serializers.SlugRelatedField(
        slug_field='slug',
        queryset=Genre.objects.all(),
        many=True,
        required=False
    )
    category = serializers.SlugRelatedField(
        slug_field='slug',
        queryset=Category.objects.all(),
    )

    class Meta:
        model = Title
        fields = ('__all__')

    def validate_year(self, value):
        """Проверяем что произведение не из будущего"""
        if value > dt.date.today().year:
            raise serializers.ValidationError(
                'Год выпуска не может быть больше текущего.'
            )
        return value
