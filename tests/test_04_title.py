from http import HTTPStatus

import pytest

from tests.utils import (check_pagination, check_permissions,
                         create_categories, create_genre, create_titles)


@pytest.mark.django_db(transaction=True)
class Test04TitleAPI:

    def test_01_title_not_auth(self, client):
        response = client.get('/api/v1/titles/')
        assert response.status_code != HTTPStatus.NOT_FOUND, (
            'Эндпоинт `/api/v1/titles/` не найден.Проверьте настройки в '
            '*urls.py*.'
        )
        assert response.status_code == HTTPStatus.OK, (
            'Проверьте, что GET-запрос неавторизованного пользователя к '
            '`/api/v1/titles/` возвращает ответ со статусом 200.'
        )

    def test_02_title_admin(self, admin_client, client):
        genres = create_genre(admin_client)
        categories = create_categories(admin_client)
        url = '/api/v1/titles/'
        title_count = 0

        assert_msg = (
            f'Если POST-запрос администратора к `{url}` '
            'содержит некорректные данные - должен вернуться ответ со '
            'статусом 400.'
        )
        data = {}
        response = admin_client.post(url, data=data)
        assert response.status_code == HTTPStatus.BAD_REQUEST, assert_msg

        invalid_data = {
            'name': 'Угнать за 60 секунд',
            'year': 'дветыщи',
            'genre': [genres[1]['slug']],
            'category': categories[1]['slug'],
            'description': 'Угонял машины всю ночь и немного подустал.'
        }
        response = admin_client.post(url, data=invalid_data)
        assert response.status_code == HTTPStatus.BAD_REQUEST, assert_msg

        post_data_1 = {
            'name': 'Мост через реку Квай',
            'year': 1957,
            'genre': [genres[0]['slug'], genres[1]['slug']],
            'category': categories[0]['slug'],
            'description': 'Рон Свонсон рекомендует.'
        }
        response = admin_client.post(url, data=post_data_1)
        assert response.status_code == HTTPStatus.CREATED, (
            f'Если POST-запрос администратора к `{url}` '
            'содержит корректные данные - должен вернуться ответ со статусом '
            '201.'
        )
        title_count += 1

        post_data_2 = {
            'name': 'Хороший, плохой, злой.',
            'year': 1966,
            'genre': [genres[2]['slug']],
            'category': categories[1]['slug'],
            'description': 'Угадай ревьюера по названию фильма.'
        }
        response = admin_client.post(url, data=post_data_2)
        assert response.status_code == HTTPStatus.CREATED, (
            f'Если POST-запрос администратора к `{url}` '
            'содержит корректные данные - должен вернуться ответ со статусом '
            '201.'
        )
        title_count += 1
        assert isinstance(response.json().get('id'), int), (
            f'Проверьте, при POST-запросе администратора к `{url}` '
            'в ответе возвращаются данные созданного объекта. Сейчас поле '
            '`id` отсутствует или не является целым числом.'
        )

        response = client.get(url)
        assert response.status_code == HTTPStatus.OK, (
            'Проверьте, что GET-запрос неавторизованного пользователя к '
            f'`{url}` возвращает ответ со статусом 200.'
        )
        data = response.json()
        check_pagination(url, data, title_count)

        expected_title_names = {post_data_1['name'], post_data_2['name']}
        title_names = {element.get('name') for element in data['results']}
        assert len(expected_title_names.intersection(title_names)) == 2, (
            f'Проверьте, что для эндпоинта `{url}` настроена пагинация. '
            'Сейчас значение параметра `results` отсутствует или содержит '
            'некорректную информацию о существующих объектах.'
        )

        for element in data['results']:
            if element['name'] == post_data_1['name']:
                title = element

        assert title.get('rating') is None, (
            'Проверьте, что при GET-запросе неавторизованного '
            f'пользователя к `{url}` возвращается информация о рейтинге '
            'произведений. Если отзывов о произведении нет - значением '
            'поля `rating` должено быть `None`.'
        )
        assert title.get('category') == categories[0], (
            'Проверьте, что при GET-запросе неавторизованного '
            f'пользователя к `{url}` в ответе содержится информация о '
            'категориях произведений. Сейчас поле `category` для элементов '
            'списка `results` отсутствует или содержит некорректное значение.'
        )

        title_genres = title.get('genre', [])
        assert genres[0] in title_genres and genres[1] in title_genres, (
            'Проверьте, что при GET-запросе неавторизованного '
            f'пользователя к `{url}` в ответе содержится список жанров '
            'для каждого произведения. Сейчас поле `genres` для элементов '
            'списка `results` отсутствует или содержит некорректное значение.'
        )
        assert title.get('year') == post_data_1['year'], (
            'Проверьте, что при GET-запросе неавторизованного '
            f'пользователя к `{url}` в ответе содержится год выхода '
            'произведений. Сейчас поле `year` для элементов списка `results` '
            'отсутствует или содержит некорректное значение.'
        )
        assert title.get('description') == post_data_1['description'], (
            'Проверьте, что при GET-запросе неавторизованного '
            f'пользователя к `{url}` в ответе содержатся описания '
            'произведений. Сейчас поле `description` для элементов списка '
            '`results` отсутствует или содержит некорректное значение.'
        )

        assert isinstance(title.get('id'), int), (
            'Проверьте, что при GET-запросе неавторизованного '
            f'пользователя к `{url}` в ответе содержатся `id` произведений. '
            'Сейчас поле `id` для элементов списка `results` отсутствует или '
            'его значение не является целым числом.'
        )

        data = {
            'name': 'Титаник',
            'year': 1997,
            'genre': [genres[1]['slug']],
            'category': categories[1]['slug'],
            'description': 'Дверь выдержала бы и двоих...'
        }
        admin_client.post(url, data=data)

        response = admin_client.get(f'{url}?genre={genres[1]["slug"]}')
        data = response.json()
        assert len(data['results']) == 2, (
            f'Проверьте, что для эндпоинта `{url}` реализована возможность '
            'фильтрации по полю `genre` с использованием параметра `slug` '
            'жанра.'
        )

        response = admin_client.get(f'{url}?category={categories[0]["slug"]}')
        data = response.json()
        assert len(data['results']) == 1, (
            f'Проверьте, что для эндпоинта `{url}` реализована возможность '
            'фильтрации по полю `category` с использованием параметра `slug` '
            'категории.'
        )

        response = admin_client.get(f'{url}?year={post_data_1["year"]}')
        data = response.json()
        assert len(data['results']) == 1, (
            f'Проверьте, что для эндпоинта `{url}` реализована возможность '
            'фильтрации по полю `year` с использованием года выхода '
            'произведения.'
        )
        response = admin_client.get(f'{url}?name={post_data_1["name"]}')
        data = response.json()
        assert len(data['results']) == 1, (
            f'Проверьте, что для эндпоинта `{url}` реализована возможность '
            'фильтрации по полю `name` с использованием названия произведения.'
        )

    def test_03_titles_detail(self, client, admin_client):
        titles, categories, genres = create_titles(admin_client)
        response = client.get(f'/api/v1/titles/{titles[0]["id"]}/')
        assert response.status_code != HTTPStatus.NOT_FOUND, (
            'Эндпоинт `/api/v1/titles/{title_id}/` не найден, проверьте '
            'настройки в *urls.py*.'
        )
        assert response.status_code == HTTPStatus.OK, (
            'Проверьте, что GET-запрос неавторизованного пользователя к '
            '`/api/v1/titles/{title_id}/` возвращает ответ со статусом 200.'
        )
        data = response.json()
        assert isinstance(data.get('id'), int), (
            'Поле `id` отсутствует или содержит некорректное значение '
            'в ответе на GET-запрос неавторизованного пользователя к '
            '`/api/v1/titles/{title_id}/`.'
        )
        assert data.get('category') == categories[0], (
            'Поле `category` отсутствует или содержит некорректное значение '
            'в ответе на GET-запрос неавторизованного пользователя к '
            '`/api/v1/titles/{title_id}/`.'
        )
        assert data.get('name') == titles[0]['name'], (
            'Поле `name` отсутствует или содержит некорректное значение '
            'в ответе на GET-запрос неавторизованного пользователя к '
            '`/api/v1/titles/{title_id}/`.'
        )

        update_data = {
            'name': 'Новое название',
            'category': categories[1]['slug']
        }
        response = admin_client.patch(
            f'/api/v1/titles/{titles[0]["id"]}/', data=update_data
        )
        assert response.status_code == HTTPStatus.OK, (
            'Проверьте, что PATCH-запрос администратора к '
            '`/api/v1/titles/{title_id}/` возвращает ответ со статусом 200.'
        )
        data = response.json()
        assert data.get('name') == update_data['name'], (
            'Проверьте, что PATCH-запрос администратора к '
            '`/api/v1/titles/{title_id}/` возвращает изменённые данные '
            'произведения. Сейчас поле `name` отсутствует в ответе или '
            'содержит некорректное значение.'
        )
        response = client.get(f'/api/v1/titles/{titles[0]["id"]}/')
        data = response.json()
        assert data.get('category') == categories[1], (
            'Проверьте, что PATCH-запрос администратора к '
            '`/api/v1/titles/{title_id}/` может изменять значение поля '
            '`category` произведения.'
        )
        assert data.get('name') == update_data['name'], (
            'Проверьте, что PATCH-запрос администратора к '
            '`/api/v1/titles/{title_id}/` может изменять значение поля '
            '`name` произведения.'
        )

        response = admin_client.delete(f'/api/v1/titles/{titles[0]["id"]}/')
        assert response.status_code == HTTPStatus.NO_CONTENT, (
            'Проверьте, что DELETE-запрос администратора к '
            '`/api/v1/titles/{title_id}/` возвращает ответ со статусом 204.'
        )
        response = admin_client.get('/api/v1/titles/')
        test_data = response.json()['results']
        assert len(test_data) == len(titles) - 1, (
            'Проверьте, что DELETE-запрос администратора к '
            '`/api/v1/titles/{title_id}/` удаляет произведение из базы данных.'
        )

    def test_04_titles_name_length_validation(self, admin_client):
        genres = create_genre(admin_client)
        categories = create_categories(admin_client)
        url = '/api/v1/titles/'

        data = {
            'name': 'It`s Over 9000!' + '!' * 242,
            'year': 1989,
            'genre': [genres[0]['slug'], genres[1]['slug']],
            'category': categories[0]['slug'],
            'description': 'Dragon Ball Z'
        }
        response = admin_client.post(url, data=data)
        assert response.status_code == HTTPStatus.BAD_REQUEST, (
            'Убедитесь, что при обработке POST-запроса администратора к '
            f'`{url}` проверяется длина поля `name`: название произведения '
            'не может быть длиннее 256 символов.'
        )

        data = {
            'name': 'Мост через реку Квай',
            'year': 1957,
            'genre': [genres[0]['slug'], genres[1]['slug']],
            'category': categories[0]['slug'],
            'description': 'Рон Свонсон рекомендует.'
        }
        response = admin_client.post(url, data=data)
        assert response.status_code == HTTPStatus.CREATED, (
            f'Если POST-запрос администратора к `{url}` '
            'содержит корректные данные - должен вернуться ответ со статусом '
            '201.'
        )
        idx = response.json().get('id')
        assert idx, (
            f'Проверьте, что ответ на успешный POST-запрос к `{url}` '
            'содержит `id` созданного произведения.'
        )

        response = admin_client.patch(f'{url}{idx}/', data={
            'name': ('longname' + 'e' * 249)
        })
        assert response.status_code == HTTPStatus.BAD_REQUEST, (
            'Проверьте, что при обработке PATCH-запрос администратора к '
            f'`{url}` проверяется длина поля `name`: название произведения не '
            'может быть длиннее 256 символов.'
        )

    def test_05_titles_check_permission(self, client, user_client,
                                        moderator_client, admin_client):
        titles, categories, genres = create_titles(admin_client)
        url = '/api/v1/titles/'
        data = {
            'name': 'Зловещие мертвецы',
            'year': 1981,
            'genre': [genres[2]['slug'], genres[1]['slug']],
            'category': categories[0]['slug'],
            'description': 'This Is My Boomstick! - Ash'
        }
        check_permissions(client, url, data,
                          'неавторизованного пользователя', titles,
                          HTTPStatus.UNAUTHORIZED)
        check_permissions(user_client, url, data,
                          'пользователя с ролью `user`', titles,
                          HTTPStatus.FORBIDDEN)
        check_permissions(moderator_client, url, data, 'модератора',
                          titles, HTTPStatus.FORBIDDEN)
