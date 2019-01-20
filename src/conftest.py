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

@pytest.fixture
def mock_delete_entity(mocker):
    return mocker.patch('pdnsadm.common.views.DeleteConfirmView.delete_entity')

@pytest.fixture
def mock_messages_success(mocker):
    return mocker.patch('django.contrib.messages.success')

@pytest.fixture
def mock_create_zone(mocker):
    return mocker.patch('pdnsadm.pdns_api.pdns.create_zone')
