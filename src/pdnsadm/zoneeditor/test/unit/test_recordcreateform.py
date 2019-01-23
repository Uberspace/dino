import pytest
from django.test.utils import override_settings

from ...views import RecordCreateForm

@pytest.fixture
def create_record_data():
    return {
        'name': 'mail.example.com.',
        'rtype': 'MX',
        'ttl': '300',
        'content': '0 example.org',
    }

def test_recordcreateform(mock_create_record, create_record_data):
    form = RecordCreateForm('example.com.', data=create_record_data)
    assert not form.errors
    assert form.is_valid()
    mock_create_record.assert_called_once_with(
        zone='example.com.',
        name='mail.example.com.',
        rtype='MX',
        ttl=300,
        content='0 example.org',
    )

def test_recordcreateform_name_add_zone(mock_create_record, create_record_data):
    create_record_data.update(name='mail')
    form = RecordCreateForm('example.com.', data=create_record_data)
    assert form.is_valid()
    mock_create_record.assert_called_once_with(
        zone='example.com.',
        name='mail.example.com.',
        rtype='MX',
        ttl=300,
        content='0 example.org',
    )

def test_recordcreateform_invalid_no_creation(mock_create_record):
    form = RecordCreateForm('example.com.', {'name': 'blargh--'})
    form.full_clean()
    mock_create_record.assert_not_called()

def test_recordcreateform_api_error(mocker, create_record_data):
    from pdnsadm.pdns_api import PDNSError
    m = mocker.patch('pdnsadm.pdns_api.pdns.create_record', side_effect=PDNSError('/', 400, 'broken'))
    form = RecordCreateForm('example.com.', create_record_data)
    form.full_clean()
    assert 'broken' in form.errors['__all__'][0]
    m.assert_called_once()

def test_recordcreateform_required(mock_create_record):
    form = RecordCreateForm('example.com.', {})
    assert not form.is_valid()
    assert 'required' in form.errors['name'][0]
    assert 'required' in form.errors['rtype'][0]
    assert 'required' in form.errors['ttl'][0]
    assert 'required' in form.errors['content'][0]
