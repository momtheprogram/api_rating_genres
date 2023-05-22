from http import HTTPStatus

import pytest

from tests.utils import (check_fields, check_pagination, create_comments,
                         create_reviews, create_single_comment)


@pytest.mark.django_db(transaction=True)
class Test06CommentAPI:

    def test_01_comment_not_auth(self, client, admin_client, admin,
                                 user_client, user, moderator_client,
                                 moderator):
        author_map = {
            admin: admin_client,
            user: user_client,
            moderator: moderator_client
        }
        reviews, titles = create_reviews(admin_client, author_map)
        url = '/api/v1/titles/{title_id}/reviews/{review_id}/comments/'

        response = client.get(
            url.format(title_id=titles[0]['id'], review_id=reviews[0]['id'])
        )
        assert response.status_code != HTTPStatus.NOT_FOUND, (
            f'Эндпоинт `{url}` не найден. Проверьте настрокий в *urls.py*.'
        )
        assert response.status_code == HTTPStatus.OK, (
            'Проверьте, что GET-запрос неавторизованного пользователя к '
            f'`{url}` возвращает ответ со статусом 200.'
        )

    def test_02_comment(self, admin_client, admin, user_client, user,
                        moderator_client, moderator):
        author_map = {
            admin: admin_client,
            user: user_client,
            moderator: moderator_client
        }
        reviews, titles = create_reviews(admin_client, author_map)
        url = '/api/v1/titles/{title_id}/reviews/{review_id}/comments/'
        first_review_comment_cnt = 0

        data = {}
        response = user_client.post(
            url.format(title_id=titles[0]['id'], review_id=reviews[0]['id']),
            data=data
        )
        assert response.status_code == HTTPStatus.BAD_REQUEST, (
            'Если POST-запрос пользователя с ролью `user` к '
            f'`{url}` содержит некорректные данные - должен вернуться ответ '
            'со статусом 400.'
        )

        post_data = {'text': 'test comment'}
        create_single_comment(
            admin_client, titles[0]["id"], reviews[0]["id"], post_data['text']
        )
        first_review_comment_cnt += 1
        create_single_comment(
            user_client, titles[0]["id"], reviews[0]["id"], 'qwerty123'
        )
        first_review_comment_cnt += 1
        response = create_single_comment(
            moderator_client, titles[0]["id"], reviews[0]["id"], 'qwerty321'
        )
        first_review_comment_cnt += 1

        assert isinstance(response.json().get('id'), int), (
            'Проверьте, что POST-запрос авторизованного пользователя к '
            f'{url} возвращает данные созданного объекта. Сейчас поля `id` '
            'нет найдено в ответе или не является целым числом.'
        )

        response = admin_client.post(
            '/api/v1/titles/999/reviews/999/comments/', data=post_data
        )
        assert response.status_code == HTTPStatus.NOT_FOUND, (
            'Проверьте, что POST-запрос авторизованного пользователя к '
            f'комментариям под несуществующим отзывом через эндпоинт `{url}` '
            'возвращает ответ со статусом 404.'
        )

        response = user_client.get(
            url.format(title_id=titles[0]['id'], review_id=reviews[0]['id'])
        )
        assert response.status_code == HTTPStatus.OK, (
            'Проверьте, что GET-запрос авторизованного пользователя к '
            f'`{url}` возвращает ответ со статусом 200.'
        )
        data = response.json()
        check_pagination(url, data, first_review_comment_cnt)

        expected_data = {
            'text': post_data['text'],
            'author': admin.username
        }
        comment = None
        for value in data['results']:
            if value.get('text') == post_data['text']:
                comment = value
        assert comment, (
            f'Проверьте, что ответ GET-запрос к `{url}` содержит данные '
            'комментариев. В ответе не найден текст '
            'комментария.'
        )
        check_fields('comment', url, comment, expected_data)

    def test_03_comment_detail_get(self, client, admin_client, admin,
                                   user_client, user, moderator_client,
                                   moderator):
        author_map = {
            admin: admin_client,
            user: user_client,
            moderator: moderator_client
        }
        comments, reviews, titles = create_comments(admin_client, author_map)
        url = (
            '/api/v1/titles/{title_id}/reviews/'
            '{review_id}/comments/{comment_id}/'
        )
        response = client.get(
            url.format(
                title_id=titles[0]['id'],
                review_id=reviews[0]['id'],
                comment_id=comments[0]['id']
            )
        )
        assert response.status_code != HTTPStatus.NOT_FOUND, (
            f'Эндпоинт `{url}` не найден. Проверьте настройки в *urls.py*.'
        )
        assert response.status_code == HTTPStatus.OK, (
            'Проверьте, что GET-запрос неавторизованного пользователя к '
            f'`{url}` возвращает ответ со статусом 200.'
        )

        expected_data = {
            key: value for key, value in comments[0].items() if key != 'id'
        }
        data = response.json()
        check_fields('comment', url, data, expected_data, detail=True)

    def test_04_comment_detail__user_patch_delete(self, admin_client, admin,
                                                  user_client, user,
                                                  moderator_client,
                                                  moderator):
        author_map = {
            admin: admin_client,
            user: user_client,
            moderator: moderator_client
        }
        comments, reviews, titles = create_comments(admin_client, author_map)
        url = (
            '/api/v1/titles/{title_id}/reviews/'
            '{review_id}/comments/{comment_id}/'
        )

        new_data = {'text': 'Updated'}
        response = user_client.patch(
            url.format(
                title_id=titles[0]['id'],
                review_id=reviews[0]['id'],
                comment_id=comments[1]['id']
            ),
            data=new_data
        )
        assert response.status_code == HTTPStatus.OK, (
            'Проверьте, что PATCH-запрос авторизованного пользователя к '
            f'его собственному комментарию через `{url}` возвращает ответ со '
            'статусом 200.'
        )
        data = response.json()
        assert data.get('text') == new_data['text'], (
            'Проверьте, что PATCH-запрос пользователя с ролью `user` к '
            f'его собственному комментарию через `{url}` возвращает '
            'измененный комментарий. Сейчас поля `text` нет в ответе или оно '
            'содержит некорректное значение.'
        )

        response = user_client.get(
            url.format(
                title_id=titles[0]['id'],
                review_id=reviews[0]['id'],
                comment_id=comments[1]['id']
            )
        )
        assert response.status_code == HTTPStatus.OK, (
            'Проверьте, что GET-запрос авторизованного пользователя к '
            f'`{url}` возвращает ответ со статусом 200.'
        )
        data = response.json()
        assert data.get('text') == new_data['text'], (
            'Проверьте, что PATCH-запрос пользователя с ролью `user` к его '
            f'собственному комментарию через `{url}` изменяет этот '
            'комментарий.'
        )

        response = user_client.patch(
            url.format(
                title_id=titles[0]['id'],
                review_id=reviews[0]['id'],
                comment_id=comments[0]['id']
            ),
            data=new_data
        )
        assert response.status_code == HTTPStatus.FORBIDDEN, (
            'Проверьте, что PATCH-запрос пользователя с ролью `user` к '
            'чужому комментарию через `{url}` возвращает ответ со статусом '
            '403.'
        )

        response = user_client.delete(
            url.format(
                title_id=titles[0]['id'],
                review_id=reviews[0]['id'],
                comment_id=comments[1]['id']
            )
        )
        assert response.status_code == HTTPStatus.NO_CONTENT, (
            'Проверьте, что DELETE-запрос пользователя с ролью `user` к '
            f'его собственному комментарию через `{url}` возвращает ответ со '
            'статусом 204.'
        )
        response = user_client.delete(
            url.format(
                title_id=titles[0]['id'],
                review_id=reviews[0]['id'],
                comment_id=comments[1]['id']
            )
        )
        assert response.status_code == HTTPStatus.NOT_FOUND, (
            'Проверьте, что DELETE-запрос пользователя с ролью `user` к '
            f'его собственному комментарию через `{url}` удаляет этот '
            'комментарий.'
        )

        response = user_client.delete(
            url.format(
                title_id=titles[0]['id'],
                review_id=reviews[0]['id'],
                comment_id=comments[0]['id']
            )
        )
        assert response.status_code == HTTPStatus.FORBIDDEN, (
            'Проверьте, что DELETE-запрос пользователя с ролью `user` к '
            f'чужому комментарию через `{url}` возвращает ответ со статусом '
            '403.'
        )

    def test_05_comment_detail_admin_and_moderator(self, admin_client, admin,
                                                   user_client, user,
                                                   moderator_client,
                                                   moderator):
        author_map = {
            admin: admin_client,
            user: user_client,
            moderator: moderator_client
        }
        comments, reviews, titles = create_comments(admin_client, author_map)
        url = (
            '/api/v1/titles/{title_id}/reviews/'
            '{review_id}/comments/{comment_id}/'
        )

        new_data = {'text': 'rewq'}
        response = admin_client.patch(
            url.format(
                title_id=titles[0]['id'],
                review_id=reviews[0]['id'],
                comment_id=comments[1]['id']
            ),
            data=new_data
        )
        assert response.status_code == HTTPStatus.OK, (
            'Проверьте, что PATCH-запрос авторизованного пользователя к '
            f'его собственному комментарию через `{url}` возвращает ответ со '
            'статусом 200.'
        )

        for idx, (client, role) in enumerate((
                (moderator_client, 'модератора'),
                (admin_client, 'администратора')
        ), 1):
            response = client.patch(
                url.format(
                    title_id=titles[0]['id'],
                    review_id=reviews[0]['id'],
                    comment_id=comments[idx]['id']
                ),
                data=new_data
            )
            assert response.status_code == HTTPStatus.OK, (
                f'Проверьте, что PATCH-запрос {role} к  чужому комментарию '
                f'через `{url}` возвращает ответ со статусом 200.'
            )

            response = client.delete(
                url.format(
                    title_id=titles[0]['id'],
                    review_id=reviews[0]['id'],
                    comment_id=comments[idx]['id']
                )
            )
            assert response.status_code == HTTPStatus.NO_CONTENT, (
                f'Проверьте, что DELETE-запрос {role} к чужому комментарию '
                f'через `{url}` возвращает ответ со статусом 204.'
            )
            response = client.get(
                url.format(
                    title_id=titles[0]['id'],
                    review_id=reviews[0]['id'],
                    comment_id=comments[idx]['id']
                )
            )
            assert response.status_code == HTTPStatus.NOT_FOUND, (
                f'Проверьте, что DELETE-запрос {role} к чужому комментарию '
                f'через `{url}` удаляет комментарий.'
            )

    def test_06_comment_detail_not_auth(self, admin_client, admin, client,
                                        user_client, user, moderator_client,
                                        moderator):
        author_map = {
            admin: admin_client,
            user: user_client,
            moderator: moderator_client
        }
        comments, reviews, titles = create_comments(admin_client, author_map)
        url = (
            '/api/v1/titles/{title_id}/reviews/'
            '{review_id}/comments/{comment_id}/'
        )
        new_data = {'text': 'update'}

        response = client.get(
            url.format(
                title_id=titles[0]['id'],
                review_id=reviews[0]['id'],
                comment_id=comments[1]['id']
            )
        )
        assert response.status_code == HTTPStatus.OK, (
            'Проверьте, что GET-запрос неавторизованного пользователя к '
            f'`{url}` возвращает ответ со статусом 200.'
        )

        response = client.post(
            url.format(
                title_id=titles[0]['id'],
                review_id=reviews[0]['id'],
                comment_id=comments[1]['id']
            ),
            data=new_data
        )
        assert response.status_code == HTTPStatus.UNAUTHORIZED, (
            'Проверьте, что POST-запрос неавторизованного пользователя к '
            f'`{url}` возвращает ответ со статусом 401.'
        )
        response = client.patch(
            url.format(
                title_id=titles[0]['id'],
                review_id=reviews[0]['id'],
                comment_id=comments[1]['id']
            ),
            data=new_data
        )
        assert response.status_code == HTTPStatus.UNAUTHORIZED, (
            'Проверьте, что PATCH-запрос неавторизованного пользователя к '
            f'`{url}` возвращает ответ со статусом 401.'
        )
        response = client.delete(
            url.format(
                title_id=titles[0]['id'],
                review_id=reviews[0]['id'],
                comment_id=comments[1]['id']
            ),
            data=new_data
        )
        assert response.status_code == HTTPStatus.UNAUTHORIZED, (
            'Проверьте, что DELETE-запрос неавторизованного пользователя к '
            f'`{url}` возвращает ответ со статусом 401.'
        )
