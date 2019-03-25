import pytest

from ...views import RecordCreateForm


def test_recordcreateform(mock_create_record, record_data):
    form = RecordCreateForm('example.com.', data=record_data)
    assert not form.errors
    assert form.is_valid()
    mock_create_record.assert_called_once_with(
        zone='example.com.',
        name='mail.example.com.',
        rtype='MX',
        ttl=300,
        content='0 example.org.',
    )


def test_recordcreateform_name_underscore(mock_create_record, record_data):
    record_data.update(name='_some._example._thing.example.com')
    form = RecordCreateForm('example.com.', data=record_data)
    assert not form.errors
    assert form.is_valid()
    mock_create_record.assert_called_once_with(
        zone='example.com.',
        name='_some._example._thing.example.com.',
        rtype='MX',
        ttl=300,
        content='0 example.org.',
    )


def test_recordcreateform_name_short(mock_create_record, record_data):
    record_data.update(name='a.a.a.a')
    form = RecordCreateForm('example.com.', data=record_data)
    assert not form.errors
    assert form.is_valid()
    mock_create_record.assert_called_once_with(
        zone='example.com.',
        name='a.a.a.a.example.com.',
        rtype='MX',
        ttl=300,
        content='0 example.org.',
    )


def test_recordcreateform_name_wildcard(mock_create_record, record_data):
    record_data.update(name='*')
    form = RecordCreateForm('example.com.', data=record_data)
    assert not form.errors
    assert form.is_valid()
    mock_create_record.assert_called_once_with(
        zone='example.com.',
        name='*.example.com.',
        rtype='MX',
        ttl=300,
        content='0 example.org.',
    )


def test_recordcreateform_name_wildcard_sub(mock_create_record, record_data):
    record_data.update(name='*.sub')
    form = RecordCreateForm('example.com.', data=record_data)
    assert not form.errors
    assert form.is_valid()
    mock_create_record.assert_called_once_with(
        zone='example.com.',
        name='*.sub.example.com.',
        rtype='MX',
        ttl=300,
        content='0 example.org.',
    )


def test_recordcreateform_name_add_zone(mock_create_record, record_data):
    record_data.update(name='mail')
    form = RecordCreateForm('example.com.', data=record_data)
    assert form.is_valid()
    mock_create_record.assert_called_once_with(
        zone='example.com.',
        name='mail.example.com.',
        rtype='MX',
        ttl=300,
        content='0 example.org.',
    )


def test_recordcreateform_name_add_dot(mock_create_record, record_data):
    record_data.update(name='mail.example.com.')
    form = RecordCreateForm('example.com.', data=record_data)
    assert form.is_valid()
    mock_create_record.assert_called_once_with(
        zone='example.com.',
        name='mail.example.com.',
        rtype='MX',
        ttl=300,
        content='0 example.org.',
    )


@pytest.mark.parametrize('name', [
    '@',
    '',
    'example.com',   # no dot
    'example.com.',  # dot
])
def test_recordcreateform_name_apex(mock_create_record, record_data, name):
    record_data.update(name=name)
    form = RecordCreateForm('example.com.', data=record_data)
    assert form.is_valid()
    mock_create_record.assert_called_once_with(
        zone='example.com.',
        name='example.com.',
        rtype='MX',
        ttl=300,
        content='0 example.org.',
    )


def test_recordcreateform_name_lookalike(mock_create_record, record_data):
    record_data.update(name='mail.anexample.com.')
    form = RecordCreateForm('example.com.', data=record_data)
    assert form.is_valid()
    mock_create_record.assert_called_once_with(
        zone='example.com.',
        name='mail.anexample.com.example.com.',
        rtype='MX',
        ttl=300,
        content='0 example.org.',
    )


def test_recordcreateform_invalid_no_creation(mock_create_record):
    form = RecordCreateForm('example.com.', {'name': 'blargh--'})
    form.full_clean()
    mock_create_record.assert_not_called()


def test_recordcreateform_api_error(broken_create_record, record_data):
    form = RecordCreateForm('example.com.', record_data)
    form.full_clean()
    assert 'broken' in form.errors['__all__'][0]
    broken_create_record.assert_called_once()


def test_recordcreateform_required(mock_create_record):
    form = RecordCreateForm('example.com.', {})
    assert not form.is_valid()
    assert 'required' in form.errors['rtype'][0]
    assert 'required' in form.errors['ttl'][0]
    assert 'required' in form.errors['content'][0]


def test_recordcreateform_rtype_standard(mock_create_record):
    form = RecordCreateForm('example.com.')
    assert ('AAAA', 'AAAA') in form.fields['rtype'].choices
