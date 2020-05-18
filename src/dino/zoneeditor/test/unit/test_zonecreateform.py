import pytest
from django.test.utils import override_settings

from dino.synczones.models import Zone

from ...views import ZoneCreateForm


@pytest.mark.django_db
def test_zonecreateform(mock_create_zone):
    form = ZoneCreateForm(data={'name': 'example.com.'})
    assert form.is_valid()
    mock_create_zone.assert_called_once_with(name='example.com.', kind='Native', nameservers=[], masters=[])
    assert Zone.objects.filter(name='example.com.').exists()


@pytest.mark.parametrize('user', [
    pytest.lazy_fixture('user_admin'),
    pytest.lazy_fixture('user_tenant_admin'),
])
@pytest.mark.django_db
def test_zonecreateform_tenant_admin(mock_create_zone, user, tenant, other_tenant):
    form = ZoneCreateForm(user=user, data={'name': 'example.co.uk.', 'tenants': [tenant.pk]})
    assert form.is_valid()
    mock_create_zone.assert_called_once_with(name='example.co.uk.', kind='Native', nameservers=[], masters=[])
    assert Zone.objects.filter(name='example.co.uk.').exists()
    assert tenant.zones.filter(name='example.co.uk.').exists()


@pytest.mark.django_db
def test_zonecreateform_tenant_choices(mock_create_zone, user_admin, user_tenant_admin, tenant, other_tenant):
    form = ZoneCreateForm(user=user_admin)
    tenant_pks = form.fields['tenants'].queryset.values_list('pk', flat=True)
    assert tenant.pk in tenant_pks
    assert other_tenant.pk in tenant_pks

    form = ZoneCreateForm(user=user_tenant_admin)
    tenant_pks = form.fields['tenants'].queryset.values_list('pk', flat=True)
    assert tenant.pk in tenant_pks
    assert other_tenant.pk not in tenant_pks


@pytest.mark.django_db
def test_zonecreateform_tenant_other(mock_create_zone, user_tenant_admin, tenant, other_tenant):
    form = ZoneCreateForm(user=user_tenant_admin, data={'name': 'example.co.uk.', 'tenants': [other_tenant.pk]})
    assert not form.is_valid()
    mock_create_zone.assert_not_called()
    assert not Zone.objects.filter(name='example.co.uk.').exists()


@pytest.mark.django_db
def test_zonecreateform_tenant_one(mock_create_zone, user_tenant_admin, tenant):
    form = ZoneCreateForm(user=user_tenant_admin, data={'name': 'example.co.uk.', 'tenants': []})
    assert not form.is_valid()
    assert 'choose a tenant' in form.errors['tenants'][0]
    mock_create_zone.assert_not_called()
    assert not Zone.objects.filter(name='example.co.uk.').exists()


@pytest.mark.django_db
def test_zonecreateform_name_add_dot(mock_create_zone):
    form = ZoneCreateForm(data={'name': 'example.com'})  # no trailing dot
    assert form.is_valid()
    mock_create_zone.assert_called_once_with(name='example.com.', kind='Native', nameservers=[], masters=[])
    assert Zone.objects.filter(name='example.com.').exists()


@pytest.mark.django_db
def test_zonecreateform_name_underscore(mock_create_zone):
    form = ZoneCreateForm(data={'name': '_some._example._thing.example.com.'})
    assert form.is_valid()
    mock_create_zone.assert_called_once_with(name='_some._example._thing.example.com.', kind='Native', nameservers=[], masters=[])
    assert Zone.objects.filter(name='_some._example._thing.example.com.').exists()


@pytest.mark.django_db
def test_zonecreateform_settings(mock_create_zone):
    with override_settings(ZONE_DEFAULT_KIND='Master', ZONE_DEFAULT_NAMESERVERS=['ns1.example.org'], ZONE_DEFAULT_MASTERS=['1.3.3.7']):
        form = ZoneCreateForm(data={'name': 'example.com.'})
        assert form.is_valid()
    mock_create_zone.assert_called_once_with(name='example.com.', kind='Master', nameservers=['ns1.example.org'], masters=['1.3.3.7'])
    assert Zone.objects.filter(name='example.com.').exists()


@pytest.mark.django_db
def test_zonecreateform_invalid_no_creation(mock_create_zone):
    form = ZoneCreateForm({'name': 'blargh--'})
    form.full_clean()
    mock_create_zone.assert_not_called()
    assert not Zone.objects.filter(name='example.com.').exists()


@pytest.mark.django_db
def test_zonecreateform_api_error(mocker):
    from dino.pdns_api import PDNSError
    m = mocker.patch('dino.pdns_api.pdns.create_zone', side_effect=PDNSError('/', 400, 'broken'))
    form = ZoneCreateForm({'name': 'domain.com.'})
    form.full_clean()
    assert 'broken' in form.errors['__all__'][0]
    assert not Zone.objects.filter(name='example.com.').exists()
    m.assert_called_once()


def test_zonecreateform_name_required(mock_create_zone):
    form = ZoneCreateForm({})
    form.full_clean()
    assert 'required' in form.errors['name'][0]


def test_zonecreateform_name_invalid(mock_create_zone):
    form = ZoneCreateForm({'name': 'hostname'})
    assert not form.is_valid()
