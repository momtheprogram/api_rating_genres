from django.contrib import admin

from reviews.models import (
    Category,
    Genre,
    Title,
    TitleGenre,
)


class GenreAdmin(admin.ModelAdmin):
    list_display = ("pk", "name", "slug")
    prepopulated_fields = {'slug': ('name',)}


class CategoryAdmin(admin.ModelAdmin):
    list_display = ("pk", "name", "slug")
    prepopulated_fields = {'slug': ('name',)}


class TitleAdmin(admin.ModelAdmin):
    list_display = ("pk", "name", "year", "description", "category")
    list_editable = ('category',)
    search_fields = ('name',)
    list_filter = ('year', 'category',)
    empty_value_display = '-пусто-'


class TitleGenreAdmin(admin.ModelAdmin):
    list_display = ("pk", "title", "genre")


admin.site.register(Genre, GenreAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Title, TitleAdmin)
admin.site.register(TitleGenre, TitleGenreAdmin)
