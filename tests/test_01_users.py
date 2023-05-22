from http import HTTPStatus

import pytest

from tests.utils import (check_pagination,
                         invalid_data_for_user_patch_and_creation)


@pytest.mark.django_db(transaction=True)
class Test01UserAPI:

    VALID_DATA_FOR_USER_CREATION = [
        (
            {
                'username': 'TestUser_2',
                'role': 'user',
                'email': 'testuser2@yamdb.fake'
            },
            ''
        ),
        (
            {
                'username': 'TestUser_3',
                'email': 'testuser3@yamdb.fake'
            },
            'без указания роли нового пользователя '
        )
    ]
    PATCH_DATA = {
        'first_name': 'New User Firstname',
        'last_name': 'New User Lastname',
        'bio': 'new user bio'
    }

    def test_01_users_not_authenticated(self, client):
        response = client.get('/api/v1/users/')

        assert response.status_code != HTTPStatus.NOT_FOUND, (
            'Эндпоинт `/api/v1/users/` не найден. Проверьте настройки в '
            '*urls.py*.'
        )

        assert response.status_code == HTTPStatus.UNAUTHORIZED, (
            'Проверьте, что GET-запрос к `/api/v1/users/` без токена '
            'авторизации возвращается ответ со статусом 401.'
        )

    def test_02_users_username_not_authenticated(self, client, admin):
        response = client.get(f'/api/v1/users/{admin.username}/')

        assert response.status_code != HTTPStatus.NOT_FOUND, (
            'Эндпоинт `/api/v1/users/{username}/` не найден. Проверьте '
            'настройки в *urls.py*.'
        )

        assert response.status_code == HTTPStatus.UNAUTHORIZED, (
            'Проверьте, что GET-запрос `/api/v1/users/{username}/` без '
            'токена авторизации возвращает ответ со статусом 401.'
        )

    def test_03_users_me_not_authenticated(self, client):
        response = client.get('/api/v1/users/me/')

        assert response.status_code != HTTPStatus.NOT_FOUND, (
            'Эндпоинт `/api/v1/users/me/` не найден. Проверьте настройки '
            'в *urls.py*.'
        )

        assert response.status_code == HTTPStatus.UNAUTHORIZED, (
            'Проверьте, что GET-запрос `/api/v1/users/me/` без токена '
            'авторизации возвращает ответ со статусом 401.'
        )

    def test_04_users_get_admin(self, admin_client, admin):
        response = admin_client.get('/api/v1/users/')
        assert response.status_code != HTTPStatus.NOT_FOUND, (
            'Эндпоинт `/api/v1/users/` не найден. Проверьте настройки в '
            '*urls.py*.'
        )
        assert response.status_code == HTTPStatus.OK, (
            'Проверьте, что GET-запрос к `/api/v1/users/` с токеном '
            'авторизации возвращает ответ со статусом 200.'
        )
        data = response.json()
        admin_data = {
            'username': admin.username,
            'email': admin.email,
            'first_name': admin.first_name,
            'last_name': admin.last_name,
            'bio': admin.bio,
            'role': admin.role
        }
        check_pagination('/api/v1/users/', data, 1, admin_data)

    def test_04_02_users_get_search(self, user, admin_client,
                                    admin, django_user_model):
        url = '/api/v1/users/'
        search_url = f'{url}?search={admin.username}'
        response = admin_client.get(search_url)
        assert response.status_code != HTTPStatus.NOT_FOUND, (
            'Эндпоинт `/api/v1/users/?search={username}` не найден. '
            'Проверьте настройки в *urls.py*.'
        )
        reponse_json = response.json()
        assert ('results' in reponse_json
                and isinstance(reponse_json.get('results'), list)), (
            'Проверьте, что GET-запрос к `/api/v1/users/?search={username}` '
            'возвращает результаты поиска по значению ключа `results` в виде '
            'списка.'
        )
        users_count = (
            django_user_model.objects.filter(username=admin.username).count()
        )
        assert len(reponse_json['results']) == users_count, (
            'Проверьте, что GET-запрос к `/api/v1/users/?search={username}` '
            'возвращает данные только тех пользователей, `username` которых '
            'удовлетворяет условию поиска.'
        )
        admin_as_dict = {
            'username': admin.username,
            'email': admin.email,
            'role': admin.role,
            'first_name': admin.first_name,
            'last_name': admin.last_name,
            'bio': admin.bio
        }
        assert reponse_json['results'] == [admin_as_dict], (
            'Проверьте, что ответ на GET-запрос к '
            '`/api/v1/users/?search={username}` содержит полный перечень '
            'данных пользователя. Ответ должен содержать следующие ключи с '
            f'корректными данными: {", ".join(admin_as_dict.keys())}.'
        )

    def test_04_01_users_get_admin_only(self, user_client, moderator_client):
        url = '/api/v1/users/'
        for client in (user_client, moderator_client):
            response = client.get(url)
            assert response.status_code != HTTPStatus.NOT_FOUND, (
                f'Эндпоинт `{url}` не найден. Проверьте настройки в '
                '*urls.py*.'
            )
            assert response.status_code == HTTPStatus.FORBIDDEN, (
                f'Проверьте, что GET-запрос к `{url}` от пользователя, не '
                'являющегося администратором, возвращает ответ со статусом '
                '403.'
            )

    def test_05_01_users_post_admin_bad_requests(self, admin_client, admin):
        empty_data = {}
        response = admin_client.post('/api/v1/users/', data=empty_data)
        assert response.status_code == HTTPStatus.BAD_REQUEST, (
            'Если POST-запрос администратора к `/api/v1/users/` '
            'не содержит необходимых данных - должен вернуться ответ со '
            'статусом 400.'
        )

        no_email_data = {
            'username': 'TestUser_noemail',
            'role': 'user'
        }
        response = admin_client.post('/api/v1/users/', data=no_email_data)
        assert response.status_code == HTTPStatus.BAD_REQUEST, (
            'Если POST-запрос администратора к `/api/v1/users/` '
            'не содержит `email` - должен вернуться ответ со статусом 400.'
        )

        no_username_data = {
            'email': 'valid_email@yamdb.fake',
            'role': 'user'
        }
        response = admin_client.post('/api/v1/users/', data=no_username_data)
        assert response.status_code == HTTPStatus.BAD_REQUEST, (
            'Если POST-запрос администратора к `/api/v1/users/` '
            ' не содержит `username` - должен вернуться ответ со статусом 400.'
        )

        duplicate_email = {
            'username': 'TestUser_duplicate',
            'role': 'user',
            'email': admin.email
        }
        response = admin_client.post('/api/v1/users/', data=duplicate_email)
        assert response.status_code == HTTPStatus.BAD_REQUEST, (
            'Если в POST-запросе администратора к `/api/v1/users/` '
            'передан `email` существующего пользователя - '
            'должен вернуться ответ со статусом 400.'
        )

        duplicate_username = {
            'username': admin.username,
            'role': 'user',
            'email': 'valid_test_email@yamdb.fake'
        }
        response = admin_client.post('/api/v1/users/', data=duplicate_username)
        assert response.status_code == HTTPStatus.BAD_REQUEST, (
            'Если в POST-запросе администратора к `/api/v1/users/` '
            'передан `username` существующего пользователя '
            'должен вернуться ответ со статусом 400.'
        )

    @pytest.mark.parametrize('data,msg_modifier', VALID_DATA_FOR_USER_CREATION)
    def test_05_02_users_post_admin_user_creation(self, admin_client,
                                                  data, msg_modifier,
                                                  django_user_model):
        response = admin_client.post('/api/v1/users/', data=data)
        assert response.status_code == HTTPStatus.CREATED, (
            'Если POST-запрос администратора к `/api/v1/users/` содержит '
            f'корректные данные {msg_modifier}- должен вернуться ответ со '
            'статусом 201.'
        )
        new_user = django_user_model.objects.filter(email=data['email'])
        assert new_user.exists(), (
            'Если POST-запрос администратора, отправленный к `/api/v1/users/`'
            f', содержит корректные данные {msg_modifier}- должен быть создан '
            'новый пользователь.'
        )
        if msg_modifier:
            assert new_user.first().role == 'user', (
                'Когда администратор создаёт пользователя через POST-запрос к '
                '`/api/v1/users/` и не указывает роль для нового пользователя '
                '- пользователю должна присваиваться роль `user`.'
            )

    def test_05_03_users_post_response_has_data(self, admin_client):
        data = {
            'first_name': 'First Name',
            'last_name': 'Last Name',
            'username': 'test_username',
            'bio': 'test bio',
            'role': 'moderator',
            'email': 'testmoder2@yamdb.fake'
        }
        response = admin_client.post('/api/v1/users/', data=data)
        assert response.status_code == HTTPStatus.CREATED, (
            'Если POST-запрос администратора к `/api/v1/users/` '
            'содержит корректные данные - должен вернуться ответ со статусом '
            '201.'
        )
        response_data = response.json()
        expected_keys = (
            'first_name', 'last_name', 'username', 'bio', 'role', 'email'
        )
        for key in expected_keys:
            assert response_data.get(key) == data[key], (
                'Если POST-запрос к `/api/v1/users/` содержит корректные '
                'данные - в ответе должны содержаться данные нового '
                f'пользователя. Сейчас ключ {key} отстутствует либо содержит '
                'некорректные данные.'
            )

    def test_05_04_users_post_user_superuser(self, user_superuser_client,
                                             django_user_model):
        valid_data = {
            'username': 'TestUser_3',
            'role': 'user',
            'email': 'testuser3@yamdb.fake'
        }
        response = user_superuser_client.post(
            '/api/v1/users/', data=valid_data
        )
        assert response.status_code == HTTPStatus.CREATED, (
            'Если POST-запрос суперпользователя к `/api/v1/users/` '
            'содержит корректные данные - должен вернуться ответ со статусом '
            '201.'
        )
        users_after = (
            django_user_model.objects.filter(email=valid_data['email'])
        )
        assert users_after.exists(), (
            'Если POST-запрос суперпользователя к `/api/v1/users/` '
            'содержит корректные данные - должен быть создан новый '
            'пользователь.'
        )

    def test_06_users_username_get_admin(self, admin_client, moderator):
        response = admin_client.get(f'/api/v1/users/{moderator.username}/')
        assert response.status_code != HTTPStatus.NOT_FOUND, (
            'Эндпоинт `/api/v1/users/{username}/` не найден. Проверьте '
            'настройки в *urls.py*.'
        )
        assert response.status_code == HTTPStatus.OK, (
            'Проверьте, что GET-запрос администратора к '
            '`/api/v1/users/{username}/` возвращает ответ со статусом 200.'
        )

        response_data = response.json()
        expected_keys = (
            'first_name', 'last_name', 'username', 'bio', 'role', 'email'
        )
        for key in expected_keys:
            assert response_data.get(key) == getattr(moderator, key), (
                'Проверьте, что ответ на GET-запрос администратора к '
                '`/api/v1/users/{username}/` содержит данные пользователя.'
                f'Сейчас ключ {key} отсутствует в ответе либо содержит '
                'некорректные данные.'
            )

    def test_06_users_username_get_not_admin(self, user_client,
                                             moderator_client, admin):
        for test_client in (user_client, moderator_client):
            response = test_client.get(f'/api/v1/users/{admin.username}/')
            assert response.status_code != HTTPStatus.NOT_FOUND, (
                'Эндпоинт `/api/v1/users/{username}/` не найден. Проверьте '
                'настройки в *urls.py*.'
            )
            assert response.status_code == HTTPStatus.FORBIDDEN, (
                'GET-запрос пользователя, не обладающего правами '
                'администратора, отправленный к `/api/v1/users/{username}/`, '
                'должен вернуть ответ со статусом 403.'
            )

    def test_07_01_users_username_patch_admin(self, user, admin_client,
                                              django_user_model):
        data = {
            'first_name': 'Admin',
            'last_name': 'Test',
            'bio': 'description'
        }
        response = admin_client.patch(
            f'/api/v1/users/{user.username}/', data=data
        )
        assert response.status_code == HTTPStatus.OK, (
            'Если PATCH-запрос администратора, отправленный к '
            '`/api/v1/users/{username}/`, содержит корректные данные - должен '
            'вернуться ответ со статусом 200.'
        )
        user = django_user_model.objects.get(username=user.username)
        for key in data:
            assert getattr(user, key) == data[key], (
                'Проверьте, что PATCH-запрос администратора к '
                '`/api/v1/users/{username}/` может изменять данные другого '
                'пользователя.'
            )

        response = admin_client.patch(
            f'/api/v1/users/{user.username}/', data={'role': 'admin'}
        )
        assert response.status_code == HTTPStatus.OK, (
            'Проверьте, что PATCH-запрос администратора к '
            '`/api/v1/users/{username}/` может изменить роль пользователя'
        )
        response = admin_client.patch(
            f'/api/v1/users/{user.username}/', data={'role': 'owner'}
        )
        assert response.status_code == HTTPStatus.BAD_REQUEST, (
            'Если в PATCH-запросе администратора к '
            '`/api/v1/users/{username}/` передана несуществующая роль - '
            'должен вернуться ответ со статусом 400.'
        )

    def check_user_data_not_changed_with_patch(self, user, client_role):
        if user:
            for key in self.PATCH_DATA:
                assert getattr(user, key) != self.PATCH_DATA[key], (
                    f'Проверьте, что PATCH-запрос {client_role} к '
                    '`/api/v1/users/{username}/` для профиля другого '
                    'пользователя не изменяет данные этого пользователя.'
                )
        else:
            raise AssertionError(
                f'Проверьте, что PATCH-запрос {client_role} к '
                '`/api/v1/users/{username}/` для профиля другого '
                'пользователя не удаляет этого пользователя.'
            )

    def test_07_02_users_username_patch_moderator(self,
                                                  moderator_client,
                                                  user,
                                                  django_user_model):
        response = moderator_client.patch(
            f'/api/v1/users/{user.username}/', data=self.PATCH_DATA
        )
        assert response.status_code == HTTPStatus.FORBIDDEN, (
            'Проверьте, что PATCH-запрос модератора к '
            '`/api/v1/users/{username}/` для профиля другого пользователя '
            'возвращает ответ со статусом 403.'
        )

        user = (
            django_user_model.objects.filter(username=user.username).first()
        )
        self.check_user_data_not_changed_with_patch(user, 'модератора')

    def test_07_03_users_username_patch_user(self, user_client, user,
                                             django_user_model):
        response = user_client.patch(
            f'/api/v1/users/{user.username}/', data=self.PATCH_DATA
        )
        assert response.status_code == HTTPStatus.FORBIDDEN, (
            'Проверьте, что PATCH-запрос пользователя с ролью `user` к '
            '`/api/v1/users/{username}/` возвращает ответ со статусом 403.'
        )

        user = (
            django_user_model.objects.filter(username=user.username).first()
        )
        self.check_user_data_not_changed_with_patch(
            user, 'пользователя с ролью `user`'
        )

    def test_07_05_users_username_put_not_allowed(self, admin_client, user):
        response = admin_client.put(
            f'/api/v1/users/{user.username}/', data=self.PATCH_DATA
        )
        assert response.status_code == HTTPStatus.METHOD_NOT_ALLOWED, (
            'Проверьте, что PUT-запрос к `/api/v1/users/{username}/` '
            'не предусмотрен и возвращает статус 405.'
        )

    def test_08_01_users_username_delete_admin(self, user, admin_client,
                                               django_user_model):
        users_cnt = django_user_model.objects.count()
        response = admin_client.delete(f'/api/v1/users/{user.username}/')
        assert response.status_code == HTTPStatus.NO_CONTENT, (
            'Проверьте, что DELETE-запрос администратора к '
            '`/api/v1/users/{username}/` возвращает ответ со статусом 204.'
        )
        assert django_user_model.objects.count() == (users_cnt - 1), (
            'Проверьте, что DELETE-запрос администратора к '
            '`/api/v1/users/{username}/` удаляет пользователя.'
        )

    def test_08_02_users_username_delete_moderator(self, moderator_client,
                                                   user, django_user_model):
        users_cnt = django_user_model.objects.count()
        response = moderator_client.delete(f'/api/v1/users/{user.username}/')
        assert response.status_code == HTTPStatus.FORBIDDEN, (
            'Проверьте, что DELETE-запрос модератора к '
            '`/api/v1/users/{username}/` возвращает ответ со статусом 403.'
        )
        assert django_user_model.objects.count() == users_cnt, (
            'Проверьте, что DELETE-запрос модератора к '
            '`/api/v1/users/{username}/` не удаляет пользователя.'
        )

    def test_08_03_users_username_delete_user(self, user_client, user,
                                              django_user_model):
        users_cnt = django_user_model.objects.count()
        response = user_client.delete(f'/api/v1/users/{user.username}/')
        assert response.status_code == HTTPStatus.FORBIDDEN, (
            'Проверьте, что DELETE-запрос пользователя с ролью `user` к '
            '`/api/v1/users/{username}/` возвращает ответ со статусом 403.'
        )
        assert django_user_model.objects.count() == users_cnt, (
            'Проверьте, что DELETE-запрос пользователя с ролью `user` к'
            '`/api/v1/users/{username}/` не удаляет пользователя.'
        )

    def test_08_04_users_username_delete_superuser(self, user_superuser_client,
                                                   user, django_user_model):
        users_cnt = django_user_model.objects.count()
        response = user_superuser_client.delete(
            f'/api/v1/users/{user.username}/'
        )
        assert response.status_code == HTTPStatus.NO_CONTENT, (
            'Проверьте, что DELETE-запрос суперпользователя к '
            '`/api/v1/users/{username}/` возвращает ответ со статусом 204.'
        )
        assert django_user_model.objects.count() == (users_cnt - 1), (
            'Проверьте, что DELETE-запрос суперпользователя к '
            '`/api/v1/users/{username}/` удаляет пользователя.'
        )

    def test_09_users_me_get(self, user_client, user):
        response = user_client.get('/api/v1/users/me/')
        assert response.status_code == HTTPStatus.OK, (
            'Проверьте, что GET-запрос обычного пользователя к '
            '`/api/v1/users/me/` возвращает ответ со статусом 200.'
        )

        response_data = response.json()
        expected_keys = ('username', 'role', 'email', 'bio')
        for key in expected_keys:
            assert response_data.get(key) == getattr(user, key), (
                'Проверьте, что GET-запрос к `/api/v1/users/me/` возвращает '
                'данные пользователя в неизмененном виде. Сейчас ключ '
                f'`{key}` отсутствует либо содержит некорректные данные.'
            )

    def test_09_02_users_me_delete_not_allowed(self, user_client, user,
                                               django_user_model):
        response = user_client.delete('/api/v1/users/me/')
        assert response.status_code == HTTPStatus.METHOD_NOT_ALLOWED, (
            'Проверьте, что DELETE-запрос к `/api/v1/users/me/` возвращает '
            'ответ со статусом 405.'
        )
        user = (
            django_user_model.objects.filter(username=user.username).first()
        )
        assert user, (
            'Проверьте, что DELETE-запрос к `/api/v1/users/me/` не удаляет '
            'пользователя.'
        )

    def test_10_01_users_me_patch(self, django_user_model, admin_client,
                                  admin, moderator_client, moderator,
                                  user_client, user):
        data = {'bio': 'description'}

        for client, user in (
                (admin_client, admin),
                (moderator_client, moderator),
                (user_client, user)
        ):
            response = client.patch('/api/v1/users/me/', data=data)
            assert response.status_code == HTTPStatus.OK, (
                'Проверьте, что PATCH-запрос к `/api/v1/users/me/` доступен '
                'пользователям всех ролей и возвращает ответ со статусом 200.'
            )
            user = django_user_model.objects.filter(
                username=user.username
            ).first()
            assert user.bio == data['bio'], (
                'Проверьте, что PATCH-запрос к `/api/v1/users/me/` изменяет '
                'данные пользователя.'
            )

    @pytest.mark.parametrize(
        'data,messege', invalid_data_for_user_patch_and_creation
    )
    def test_10_02_users_me_has_field_validation(self, user_client, data,
                                                 messege):
        url = '/api/v1/users/me/'
        request_method = 'PATCH'
        response = user_client.patch(url, data=data)
        assert response.status_code == HTTPStatus.BAD_REQUEST, (
            messege[0].format(url=url, request_method=request_method)
        )

    def test_10_03_users_me_patch_change_role_not_allowed(self,
                                                          user_client,
                                                          user,
                                                          django_user_model):
        data = {
            'first_name': 'New user first name',
            'last_name': 'New user last name',
            'bio': 'new user bio',
        }
        response = user_client.patch('/api/v1/users/me/', data=data)
        assert response.status_code == HTTPStatus.OK, (
            'Проверьте, что PATCH-запрос пользователя с ролью `user` к '
            '`/api/v1/users/me/` возвращает ответ со статусом 200.'
        )

        current_role = user.role
        data = {
            'role': 'admin'
        }
        response = user_client.patch('/api/v1/users/me/', data=data)
        user = django_user_model.objects.filter(username=user.username).first()
        assert user.role == current_role, (
            'Проверьте, что PATCH-запрос к `/api/v1/users/me/` с ключом '
            '`role` не изменяет роль пользователя.'
        )
