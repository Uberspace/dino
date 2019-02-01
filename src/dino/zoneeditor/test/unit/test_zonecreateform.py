from django.test.utils import override_settings

from ...views import ZoneCreateForm


def test_zonecreateform(mock_create_zone):
    form = ZoneCreateForm(data={'name': 'example.com.'})
    assert form.is_valid()
    mock_create_zone.assert_called_once_with(name='example.com.', kind='Native', nameservers=[])


def test_zonecreateform_name_add_dot(mock_create_zone):
    form = ZoneCreateForm(data={'name': 'example.com'})  # no trailing dot
    assert form.is_valid()
    mock_create_zone.assert_called_once_with(name='example.com.', kind='Native', nameservers=[])


def test_zonecreateform_settings(mock_create_zone):
    with override_settings(ZONE_DEFAULT_KIND='Master', ZONE_DEFAULT_NAMESERVERS=['ns1.example.org']):
        form = ZoneCreateForm(data={'name': 'example.com.'})
        assert form.is_valid()
    mock_create_zone.assert_called_once_with(name='example.com.', kind='Master', nameservers=['ns1.example.org'])


def test_zonecreateform_invalid_no_creation(mock_create_zone):
    form = ZoneCreateForm({'name': 'blargh--'})
    form.full_clean()
    mock_create_zone.assert_not_called()


def test_zonecreateform_api_error(mocker):
    from dino.pdns_api import PDNSError
    m = mocker.patch('dino.pdns_api.pdns.create_zone', side_effect=PDNSError('/', 400, 'broken'))
    form = ZoneCreateForm({'name': 'domain.com.'})
    form.full_clean()
    assert 'broken' in form.errors['__all__'][0]
    m.assert_called_once()


def test_zonecreateform_name_required(mock_create_zone):
    form = ZoneCreateForm({})
    form.full_clean()
    assert 'required' in form.errors['name'][0]


def test_zonecreateform_name_invalid(mock_create_zone):
    form = ZoneCreateForm({'name': 'hostname'})
    assert not form.is_valid()
