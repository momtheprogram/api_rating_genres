from http import HTTPStatus

import pytest

from tests.utils import (check_name_and_slug_patterns, check_pagination,
                         check_permissions, create_genre)


@pytest.mark.django_db(transaction=True)
class Test03GenreAPI:

    def test_01_genre_not_auth(self, client):
        response = client.get('/api/v1/genres/')
        assert response.status_code != HTTPStatus.NOT_FOUND, (
            'Эндпоинт `/api/v1/genres/` не найден. Проверьте настройки в '
            '*urls.py*.'
        )
        assert response.status_code == HTTPStatus.OK, (
            'Проверьте, что GET-запрос неавторизованного пользователя к  '
            '`/api/v1/genres/` возвращает ответ со статусом 200.'
        )

    def test_02_genre(self, admin_client, client):
        genres_count = 0
        url = '/api/v1/genres/'

        data = {}
        response = admin_client.post(url, data=data)
        assert response.status_code == HTTPStatus.BAD_REQUEST, (
            f'Если POST-запрос администратора к `{url}` '
            'содержит некорректные данные - должен вернуться ответ со '
            'статусом 400.'
        )

        data = {'name': 'Ужасы', 'slug': 'horror'}
        response = admin_client.post(url, data=data)
        assert response.status_code == HTTPStatus.CREATED, (
            f'Если POST-запрос администратора к `{url}` содержит корректные '
            'данные - должен вернуться ответ со статусом 201.'
        )
        genres_count += 1

        data = {'name': 'Триллер', 'slug': 'horror'}
        response = admin_client.post(url, data=data)
        assert response.status_code == HTTPStatus.BAD_REQUEST, (
            f'Если в POST-запросе администратора, отправленном к `{url}`, '
            'передан уже существующий `slug` - должен вернуться ответ со '
            'статусом 400.'
        )

        post_data = {'name': 'Комедия', 'slug': 'comedy'}
        response = admin_client.post(url, data=post_data)
        assert response.status_code == HTTPStatus.CREATED, (
            f'Если POST-запрос администратора, отправленный к `{url}`, '
            'содержит корректные данные - должен вернуться ответ со статусом '
            '201.'
        )
        genres_count += 1

        response = client.get(url)
        assert response.status_code == HTTPStatus.OK, (
            'Проверьте, что GET-запрос неавторизованного пользователя к '
            f'`{url}` возвращает ответ со статусом 200.'
        )
        data = response.json()
        check_pagination(url, data, genres_count, post_data)

        response = admin_client.get(f'{url}?search={post_data["name"]}')
        data = response.json()
        assert len(data['results']) == 1, (
            f'Проверьте, что GET-запрос к `{url}?search=<name>` возвращает '
            'данные только тех жанров, поле `name` которых удовлетворяет '
            'условию поиска.'
        )

    @pytest.mark.parametrize('data,massage', check_name_and_slug_patterns)
    def test_03_category_fields_validation(self, data, massage, admin_client):
        url = '/api/v1/genres/'
        response = admin_client.post(url, data=data)
        assert response.status_code == HTTPStatus.BAD_REQUEST, (
            massage[0].format(url=url)
        )

    def test_04_genres_delete(self, admin_client):
        genres = create_genre(admin_client)
        response = admin_client.delete(f'/api/v1/genres/{genres[0]["slug"]}/')
        assert response.status_code == HTTPStatus.NO_CONTENT, (
            'Проверьте, что DELETE-запрос администратора к '
            '`/api/v1/genres/{slug}/` возвращает ответ со  статусом 204.'
        )
        response = admin_client.get('/api/v1/genres/')
        test_data = response.json()['results']
        assert len(test_data) == len(genres) - 1, (
            'Проверьте, что DELETE-запрос администратора к '
            '`/api/v1/genres/{slug}/` удаляет жанр из БД.'
        )
        response = admin_client.get(f'/api/v1/genres/{genres[0]["slug"]}/')
        assert response.status_code == HTTPStatus.METHOD_NOT_ALLOWED, (
            'Проверьте, что GET-запрос администратора к '
            '`/api/v1/genres/{slug}/` возвращает ответ со статусом 405.'
        )
        response = admin_client.patch(f'/api/v1/genres/{genres[0]["slug"]}/')
        assert response.status_code == HTTPStatus.METHOD_NOT_ALLOWED, (
            'Проверьте, что PATCH-запрос администратора к '
            '`/api/v1/genres/{slug}/` возвращает ответ со статусом 405.'
        )

    def test_05_genres_check_permission(self, client,
                                        user_client,
                                        moderator_client,
                                        admin_client):
        genres = create_genre(admin_client)
        data = {
            'name': 'Боевик',
            'slug': 'action'
        }
        url = '/api/v1/genres/'
        check_permissions(client, url, data, 'неавторизованного пользователя',
                          genres, HTTPStatus.UNAUTHORIZED)
        check_permissions(user_client, url, data,
                          'пользователя с ролью `user`', genres,
                          HTTPStatus.FORBIDDEN)
        check_permissions(moderator_client, url, data, 'модератора',
                          genres, HTTPStatus.FORBIDDEN)
