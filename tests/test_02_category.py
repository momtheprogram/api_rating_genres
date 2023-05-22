from http import HTTPStatus

import pytest

from tests.utils import (check_name_and_slug_patterns, check_pagination,
                         check_permissions, create_categories)


@pytest.mark.django_db(transaction=True)
class Test02CategoryAPI:

    def test_01_category_not_auth(self, client):
        response = client.get('/api/v1/categories/')
        assert response.status_code != HTTPStatus.NOT_FOUND, (
            'Эндпоинт `/api/v1/categories/` не найден. Проверьте настройки в '
            '*urls.py*.'
        )
        assert response.status_code == HTTPStatus.OK, (
            'Проверьте, что GET-запрос неавторизованного пользователя к '
            '`/api/v1/categories/` возвращает ответ со статусом 200.'
        )

    def test_02_category_with_admin_user(self, admin_client):
        categories_count = 0

        url = '/api/v1/categories/'
        data = {}
        response = admin_client.post(url, data=data)
        assert response.status_code == HTTPStatus.BAD_REQUEST, (
            f'Если POST-запрос администратора, отправленный к `{url}`, '
            'содержит некорректные данные - должен вернуться ответ со '
            'статусом 400.'
        )

        data = {
            'name': 'Фильм',
            'slug': 'films'
        }
        response = admin_client.post(url, data=data)
        assert response.status_code == HTTPStatus.CREATED, (
            f'Если POST-запрос администратора, отправленный к `{url}`, '
            'содержит корректные данные - должен вернуться ответ со статусом '
            '201.'
        )
        categories_count += 1

        data = {
            'name': 'Новые фильмы',
            'slug': 'films'
        }
        response = admin_client.post(url, data=data)
        assert response.status_code == HTTPStatus.BAD_REQUEST, (
            f'Если в POST-запросе администратора к `{url}` '
            'передан уже существующий `slug` - должен вернуться ответ со '
            'статусом 400.'
        )

        post_data = {
            'name': 'Книги',
            'slug': 'books'
        }
        response = admin_client.post(url, data=post_data)
        assert response.status_code == HTTPStatus.CREATED, (
            f'Если POST-запрос администратора к `{url}` '
            'содержит корректные данные - должен вернуться ответ со статусом '
            '201.'
        )
        categories_count += 1

        response = admin_client.get(url)
        assert response.status_code == HTTPStatus.OK, (
            f'Проверьте, что при GET-запросе к `{url}` возвращается статус '
            '200.'
        )
        data = response.json()
        check_pagination(url, data, categories_count, post_data)

        response = admin_client.get(f'{url}?search={post_data["name"]}')
        data = response.json()
        assert len(data['results']) == 1, (
            f'Проверьте, что GET-запрос к `{url}?search=<name>` возвращает '
            'данные только тех категорий, поле `name` которых удовлетворяет '
            'условию поиска.'
        )

    @pytest.mark.parametrize('data,massage', check_name_and_slug_patterns)
    def test_03_category_fields_validation(self, data, massage, admin_client):
        url = '/api/v1/categories/'
        response = admin_client.post(url, data=data)
        assert response.status_code == HTTPStatus.BAD_REQUEST, (
            massage[0].format(url=url)
        )

    def test_04_category_delete_admin(self, admin_client):
        category_1, category_2 = create_categories(admin_client)
        response = admin_client.delete(
            f'/api/v1/categories/{category_1["slug"]}/'
        )
        assert response.status_code == HTTPStatus.NO_CONTENT, (
            'Проверьте, что DELETE-запрос администратора к '
            '`/api/v1/categories/{slug}/` возвращает ответ со статусом 204.'
        )
        response = admin_client.get('/api/v1/categories/')
        test_data = response.json()['results']
        assert len(test_data) == 1, (
            'Проверьте, что DELETE-запрос администратора к '
            '`/api/v1/categories/{slug}/` удаляет категорию.'
        )

        response = admin_client.get(
            f'/api/v1/categories/{category_2["slug"]}/'
        )
        assert response.status_code == HTTPStatus.METHOD_NOT_ALLOWED, (
            'Проверьте, что GET-запросы к `/api/v1/categories/{slug}/` '
            'запрещены и возвращают ответ со статусом 405.'
        )
        response = admin_client.patch(
            f'/api/v1/categories/{category_2["slug"]}/'
        )
        assert response.status_code == HTTPStatus.METHOD_NOT_ALLOWED, (
            'Проверьте, что PATCH-запросы к `/api/v1/categories/{slug}/` '
            'запрещены и возвращают ответ со статусом 405.'
        )

    def test_05_category_check_permission_admin(self, client,
                                                user_client,
                                                moderator_client,
                                                admin_client):
        categories = create_categories(admin_client)
        data = {
            'name': 'Музыка',
            'slug': 'music'
        }
        url = '/api/v1/categories/'
        check_permissions(client, url, data, 'неавторизованного пользователя',
                          categories, HTTPStatus.UNAUTHORIZED)
        check_permissions(user_client, url, data,
                          'пользователя с ролью `user`', categories,
                          HTTPStatus.FORBIDDEN)
        check_permissions(moderator_client, url, data, 'модератора',
                          categories, HTTPStatus.FORBIDDEN)
