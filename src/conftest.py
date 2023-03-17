import os
import sys

import pytest
from django.contrib.auth import get_user_model
from django.core import signing
from django.core.management import call_command
from django.test import Client

from dino.pdns_api import PDNSError


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
def mock_pdns_get_records(mocker):
    rval = [
        {'name': r[0], 'ttl': r[1], 'rtype': r[2], 'content': r[3]}
        for r in [
            ('mail.example.com.', 300, 'A', '1.2.3.4'),
            ('example.com.', 300, 'MX', '0 mail.example.org.'),
        ] + [(f'r{i}.example.com.', 300, 'A', '4.3.2.1') for i in range(500)]
    ] + [{'name': 'example.com', 'ttl': 300, 'rtype': 'SOA', 'content': 'a.misconfigured.powerdns.server. hostmaster.example.com. 2019031306 10800 3600 604800 3601'}]
    return mocker.patch('dino.pdns_api.pdns.get_records', return_value=rval)


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
def mock_update_record(mocker):
    return mocker.patch('dino.pdns_api.pdns.update_record')


@pytest.fixture
def broken_create_record(mocker):
    return mocker.patch('dino.pdns_api.pdns.create_record', side_effect=PDNSError('/', 400, 'broken'))


@pytest.fixture
def mock_delete_record(mocker):
    return mocker.patch('dino.pdns_api.pdns.delete_record')


@pytest.fixture
def broken_delete_record(mocker):
    return mocker.patch('dino.pdns_api.pdns.delete_record', side_effect=PDNSError('/', 400, 'broken'))


@pytest.fixture
def mock_pdns_get_zones(mocker):
    rval = [
        'example.com.',
        'example.org.',
    ] + [f'example{i}.org' for i in range(500)] + ['localhost.']
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


@pytest.fixture
def record_data():
    return {
        'name': 'mail.example.com.',
        'rtype': 'MX',
        'ttl': 300,
        'content': '0 example.org.',
    }


@pytest.fixture
def signed_record_data(record_data):
    return signing.dumps(record_data)
