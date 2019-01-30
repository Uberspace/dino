from collections import namedtuple

import pytest
from django.contrib.auth import get_user_model
from django.core import signing
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
def tenant(db_zone):
  from pdnsadm.tenants.models import Tenant
  tenant = Tenant.objects.create(name="some tenant")
  tenant.zones.add(db_zone)
  return tenant

@pytest.fixture
def user_tenant(tenant):
  user = get_user_model().objects.create(
    username='tenanteduser',
  )
  tenant.users.add(user)
  return user

@pytest.fixture
def client_user_tenant(client, user_tenant):
  client.force_login(user_tenant)
  return client

@pytest.fixture
def user_no_tenant():
  User = get_user_model()
  return User.objects.create(
    username='user',
  )

@pytest.fixture
def client_user_no_tenant(client, user_no_tenant):
  client.force_login(user_no_tenant)
  return client

@pytest.fixture
def db_zone():
  from pdnsadm.synczones.models import Zone
  return Zone.objects.create(
    name='example.com',
  )

@pytest.fixture
def mock_delete_entity(mocker):
    return mocker.patch('pdnsadm.common.views.DeleteConfirmView.delete_entity')

@pytest.fixture
def mock_messages_success(mocker):
    return mocker.patch('django.contrib.messages.success')

@pytest.fixture
def mock_messages_error(mocker):
    return mocker.patch('django.contrib.messages.error')

@pytest.fixture
def mock_create_zone(mocker):
    return mocker.patch('pdnsadm.pdns_api.pdns.create_zone')

@pytest.fixture
def mock_create_record(mocker):
    return mocker.patch('pdnsadm.pdns_api.pdns.create_record')

@pytest.fixture
def mock_pdns_get_zones(mocker):
    MockPDNSZone = namedtuple('MockPDNSZone', ['name'])
    rval = [
        MockPDNSZone('example.com'),
        MockPDNSZone('example.org'),
    ] + [MockPDNSZone(f'example{i}.org') for i in range(500)]
    return mocker.patch('pdnsadm.pdns_api.pdns.get_zones', return_value=rval)

@pytest.fixture
def mock_pdns_delete_zone(mocker):
    return mocker.patch('pdnsadm.pdns_api.pdns.delete_zone')

@pytest.fixture
def mock_pdns_delete_record(mocker):
    return mocker.patch('pdnsadm.pdns_api.pdns.delete_record')

@pytest.fixture
def signed_zone_name():
    return signing.dumps('example.com.')
