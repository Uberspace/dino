import pytest
from django.contrib.auth import get_user_model
from django.test import Client


@pytest.fixture
def client():
  return Client()

@pytest.fixture
def user_admin():
  User = get_user_model()
  return User.objects.create(
    username='admin',
    is_superuser=True,
  )

@pytest.fixture
def client_admin(client, user_admin):
  client.force_login(user_admin)
  return client
