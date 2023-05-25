from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


MAX_TITLE_LENGTH = 200
MAX_STR_TEXT_LIMIT = 15


class Category(models.Model):
    """Модель катерогий"""
    name = models.CharField(
        max_length=MAX_TITLE_LENGTH,
        unique=True,
        verbose_name='Категория'
    )
    slug = models.SlugField(
        unique=True,
        db_index=True,
        verbose_name='URL'
    )

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'

    def __str__(self):
        return self.name[:MAX_STR_TEXT_LIMIT]


class Genre(models.Model):
    """Модель жанров"""
    name = models.CharField(
        'Жанр',
        max_length=MAX_TITLE_LENGTH,
        unique=True,
    )
    slug = models.SlugField(
        unique=True,
        db_index=True,
        verbose_name='URL'
    )

    class Meta:
        verbose_name = 'Жанр'
        verbose_name_plural = 'Жанры'

    def __str__(self):
        return self.name[:MAX_STR_TEXT_LIMIT]


class Title(models.Model):
    """Модель произведений"""
    name = models.CharField(
        'Название',
        max_length=MAX_TITLE_LENGTH,
    )
    year = models.IntegerField('Год выпуска',)
    description = models.TextField('Описание',)
    genre = models.ManyToManyField(
        Genre,
        through='TitleGenre',
        related_name='titles',
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        related_name='titles',
        verbose_name='Категория',
    )

    class Meta:
        verbose_name = 'Произведение'
        verbose_name_plural = 'Произведения'

    def __str__(self):
        return self.name[:MAX_STR_TEXT_LIMIT]


class TitleGenre(models.Model):
    """Модель для связи многие ко многим"""
    title = models.ForeignKey(
        Title,
        on_delete=models.CASCADE
    )
    genre = models.ForeignKey(
        Genre,
        on_delete=models.CASCADE
    )

    class Meta:
        constraints = (
            models.UniqueConstraint(
                fields=('title', "genre"),
                name='title_genre_constraint'),
        )

    def __str__(self):
        return (
            f'{self.title.name[:MAX_STR_TEXT_LIMIT]}'
            f'{self.genre.name[:MAX_STR_TEXT_LIMIT]}'
        )
    

class Review(models.Model):
    """Модель с отзывами."""
    title = models.ForeignKey(
        Title,
        on_delete=models.CASCADE,
        related_name='reviews'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='reviews'
    )
    pub_date = models.DateTimeField(
        'Дата публикации отзыва',
        auto_now_add=True,
        db_index=True
    )
    text = models.TextField()
    score = models.IntegerField(
        'Оценка',
        default=0,
        validators=[
            MinValueValidator(1),
            MaxValueValidator(10)
        ]
    )

    class Meta:
        ordering = ['-pub_date'],
        constrains = [
            models.UniqueConstraint(
                fields=['author', 'title'],
                name='unique_review'
            )
        ]


class Comment(models.Model):
    """"Модель с комментариями."""
    review = models.ForeignKey(
        Review,
        on_delete=models.CASCADE,
        related_name='comments'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comments'
    )
    pub_date = models.DateTimeField(
        'Дата комментария', 
        auto_now_add=True,
        db_index=True
    )
    text = models.TextField()

    def __str__(self):
        return self.author

