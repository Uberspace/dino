import os
import sys
from collections import namedtuple

import pytest
from django.contrib.auth import get_user_model
from django.core import signing
from django.core.management import call_command
from django.test import Client


@pytest.fixture(scope="session", autouse=True)
def collect_static(request):
    oldstdout = sys.stdout

    try:
        sys.stdout = open(os.devnull, 'w')
        call_command('collectstatic', '--noinput', '--clear')
    finally:
        sys.stdout = oldstdout


@pytest.fixture
def base_client():
    return Client()


@pytest.fixture
def user_admin():
    User = get_user_model()
    return User.objects.create(
      username='admin',
      is_superuser=True,
    )


@pytest.fixture
def client_admin(base_client, user_admin):
    base_client.force_login(user_admin)
    return base_client


@pytest.fixture
def tenant(db_zone):
    from dino.tenants.models import Tenant
    tenant = Tenant.objects.create(name="some tenant")
    tenant.zones.add(db_zone)
    return tenant


@pytest.fixture
def other_tenant():
    from dino.tenants.models import Tenant
    tenant = Tenant.objects.create(name="some other tenant")
    return tenant


@pytest.fixture
def user_tenant_admin(tenant):
    from dino.tenants.models import PermissionLevels
    user = get_user_model().objects.create(
      username='tenanteduser',
    )
    tenant.users.add(user, through_defaults={'level': PermissionLevels.ADMIN})
    return user


@pytest.fixture
def client_user_tenant_admin(base_client, user_tenant_admin):
    base_client.force_login(user_tenant_admin)
    return base_client


@pytest.fixture
def user_tenant_user(tenant):
    from dino.tenants.models import PermissionLevels
    user = get_user_model().objects.create(
      username='tenanteduser',
    )
    tenant.users.add(user, through_defaults={'level': PermissionLevels.USER})
    return user


@pytest.fixture
def client_user_tenant_user(base_client, user_tenant_user):
    base_client.force_login(user_tenant_user)
    return base_client


@pytest.fixture
def user_no_tenant():
    User = get_user_model()
    return User.objects.create(
      username='user',
    )


@pytest.fixture
def client_user_no_tenant(base_client, user_no_tenant):
    base_client.force_login(user_no_tenant)
    return base_client


@pytest.fixture
def db_zone():
    from dino.synczones.models import Zone
    Zone.objects.create(
      name='example.org.',
    )
    return Zone.objects.create(
      name='example.com.',
    )


@pytest.fixture
def mock_delete_entity(mocker):
    return mocker.patch('dino.common.views.DeleteConfirmView.delete_entity')


@pytest.fixture
def mock_messages_success(mocker):
    return mocker.patch('django.contrib.messages.success')


@pytest.fixture
def mock_messages_error(mocker):
    return mocker.patch('django.contrib.messages.error')


@pytest.fixture
def mock_create_zone(mocker):
    return mocker.patch('dino.pdns_api.pdns.create_zone')


@pytest.fixture
def mock_create_record(mocker):
    return mocker.patch('dino.pdns_api.pdns.create_record')


@pytest.fixture
def MockPDNSZone():
    return namedtuple('MockPDNSZone', ['name'])


@pytest.fixture
def mock_pdns_get_zones(mocker, MockPDNSZone):
    rval = [
        MockPDNSZone('example.com.'),
        MockPDNSZone('example.org.'),
    ] + [MockPDNSZone(f'example{i}.org') for i in range(500)]
    return mocker.patch('dino.pdns_api.pdns.get_zones', return_value=rval)


@pytest.fixture
def mock_pdns_delete_zone(mocker):
    return mocker.patch('dino.pdns_api.pdns.delete_zone')


@pytest.fixture
def mock_pdns_delete_record(mocker):
    return mocker.patch('dino.pdns_api.pdns.delete_record')


@pytest.fixture
def signed_example_com():
    return signing.dumps('example.com.')


@pytest.fixture
def signed_example_org():
    return signing.dumps('example.org.')
