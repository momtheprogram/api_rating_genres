import csv
import logging
import sys

from django.core.management.base import BaseCommand

from reviews.models import Category, Comment, Genre, Review, Title, TitleGenre, User


CSV_PATH = 'static/data/'
FOREIGN_KEY_FIELDS = ('category', 'author')

TABLES = {
    User: 'users.csv',
    Genre: 'genre.csv',
    Category: 'category.csv',
    Title: 'titles.csv',
    TitleGenre: 'genre_title.csv',
    Review: 'review.csv',
    Comment: 'comments.csv',
}

logging.basicConfig( 
    level=logging.INFO, 
    handlers=[ 
        logging.StreamHandler(sys.stdout) 
    ], 
    format=( 
        '%(asctime)s - ' 
        '%(levelname)s - ' 
        '%(message)s' 
    ) 
) 


def csv_import(csv_data, model):
    objects = []
    for row in csv_data:
        for field in FOREIGN_KEY_FIELDS:
            if field in row:
                row[f'{field}_id'] = row[field]
                del row[field]
        objects.append(model(**row))
    model.objects.bulk_create(objects)


class Command(BaseCommand):
    help = 'импорт из .csv'

    def handle(self, *args, **kwargs):
        for model in TABLES:
            with open(
                CSV_PATH + TABLES[model],
                newline='',
                encoding='utf8'
            ) as csv_file:
                csv_import(csv.DictReader(csv_file), model)
                logging.info(f'Импорт данных для модели {model.__name__} завершен.')
        self.stdout.write(
            self.style.SUCCESS(
                'Загрузка завершена'
            )
        )
