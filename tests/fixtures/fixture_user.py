import pytest
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import AccessToken


@pytest.fixture
def user_superuser(django_user_model):
    return django_user_model.objects.create_superuser(
        username='TestSuperuser',
        email='testsuperuser@yamdb.fake',
        password='1234567',
        role='user',
        bio='superuser bio'
    )


@pytest.fixture
def admin(django_user_model):
    return django_user_model.objects.create_user(
        username='TestAdmin',
        email='testadmin@yamdb.fake',
        password='1234567',
        role='admin',
        bio='admin bio'
    )


@pytest.fixture
def moderator(django_user_model):
    return django_user_model.objects.create_user(
        username='TestModerator',
        email='testmoder@yamdb.fake',
        password='1234567',
        role='moderator',
        bio='moder bio'
    )


@pytest.fixture
def user(django_user_model):
    return django_user_model.objects.create_user(
        username='TestUser',
        email='testuser@yamdb.fake',
        password='1234567',
        role='user',
        bio='user bio'
    )


@pytest.fixture
def token_user_superuser(user_superuser):
    token = AccessToken.for_user(user_superuser)
    return {
        'access': str(token),
    }


@pytest.fixture
def user_superuser_client(token_user_superuser):
    client = APIClient()
    client.credentials(
        HTTP_AUTHORIZATION=f'Bearer {token_user_superuser["access"]}'
    )
    return client


@pytest.fixture
def token_admin(admin):
    token = AccessToken.for_user(admin)
    return {
        'access': str(token),
    }


@pytest.fixture
def admin_client(token_admin):
    client = APIClient()
    client.credentials(HTTP_AUTHORIZATION=f'Bearer {token_admin["access"]}')
    return client


@pytest.fixture
def token_moderator(moderator):
    token = AccessToken.for_user(moderator)
    return {
        'access': str(token),
    }


@pytest.fixture
def moderator_client(token_moderator):
    client = APIClient()
    client.credentials(
        HTTP_AUTHORIZATION=f'Bearer {token_moderator["access"]}'
    )
    return client


@pytest.fixture
def token_user(user):
    token = AccessToken.for_user(user)
    return {
        'access': str(token),
    }


@pytest.fixture
def user_client(token_user):
    client = APIClient()
    client.credentials(HTTP_AUTHORIZATION=f'Bearer {token_user["access"]}')
    return client
