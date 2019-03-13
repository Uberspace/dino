from ...views import RecordEditForm


def test_recordeditform_identical(mock_create_record, mock_delete_record, record_data, signed_record_data):
    form = RecordEditForm('example.com.', data={
        'identifier': signed_record_data,
        **record_data,
    })
    assert not form.errors
    assert form.is_valid()
    mock_delete_record.assert_not_called()
    mock_create_record.assert_not_called()


def test_recordeditform_invalid(mock_create_record, mock_delete_record, record_data, signed_record_data):
    record_data['rtype'] = 'abc'
    form = RecordEditForm('example.com.', data={
        'identifier': signed_record_data,
        **record_data,
    })
    assert not form.is_valid()
    mock_delete_record.assert_not_called()
    mock_create_record.assert_not_called()


def test_recordeditform_api_error_create(broken_create_record, mock_delete_record, record_data, signed_record_data):
    record_data['rtype'] = 'AAAA'
    form = RecordEditForm('example.com.', data={
        'identifier': signed_record_data,
        **record_data,
    })
    assert not form.is_valid()
    assert 'broken' in form.errors['__all__'][0]
    assert 'create new record' in form.errors['__all__'][0]
    assert 'broken' in form.errors['__all__'][1]
    assert 're-create old record' in form.errors['__all__'][1]
    assert len(form.errors['__all__']) == 2
    assert len(broken_create_record.call_args) == 2
    broken_create_record.assert_any_call(
        zone='example.com.',
        name='mail.example.com.',
        rtype='MX',
        ttl=300,
        content='0 example.org.',
    )
    broken_create_record.assert_any_call(
        zone='example.com.',
        name='mail.example.com.',
        rtype='AAAA',
        ttl=300,
        content='0 example.org.',
    )


def test_recordeditform_api_error_delete(mock_create_record, broken_delete_record, record_data, signed_record_data):
    record_data['rtype'] = 'AAAA'
    form = RecordEditForm('example.com.', data={
        'identifier': signed_record_data,
        **record_data,
    })
    assert not form.is_valid()
    assert 'broken' in form.errors['__all__'][0]
    assert 'delete old record' in form.errors['__all__'][0]
    assert len(form.errors['__all__']) == 1
    broken_delete_record.assert_called_once()
    mock_create_record.assert_not_called()


def test_recordeditform_change(mock_create_record, mock_delete_record, record_data, signed_record_data):
    record_data['name'] = 'mail2.example.com.'
    record_data['rtype'] = 'AAAA'
    record_data['ttl'] = '300'
    record_data['content'] = '::1'
    form = RecordEditForm('example.com.', data={
        'identifier': signed_record_data,
        **record_data,
    })
    assert not form.errors
    assert form.is_valid()
    mock_delete_record.assert_called_once_with(
        zone='example.com.',
        name='mail.example.com.',
        rtype='MX',
        content='0 example.org.',
    )
    mock_create_record.assert_called_once_with(
        zone='example.com.',
        name='mail2.example.com.',
        rtype='AAAA',
        ttl=300,
        content='::1',
    )


def test_recordeditform_change_content_only(mock_create_record, mock_delete_record, record_data, signed_record_data):
    record_data['content'] = '1 example.com.'
    form = RecordEditForm('example.com.', data={
        'identifier': signed_record_data,
        **record_data,
    })
    assert not form.errors
    assert form.is_valid()
    mock_delete_record.assert_called_once_with(
        zone='example.com.',
        name='mail.example.com.',
        rtype='MX',
        content='0 example.org.',
    )
    mock_create_record.assert_called_once_with(
        zone='example.com.',
        name='mail.example.com.',
        rtype='MX',
        ttl=300,
        content='1 example.com.',
    )


def test_recordeditform_change_ttl_only(mock_create_record, mock_delete_record, mock_update_record, record_data, signed_record_data):
    record_data['ttl'] = '1337'
    form = RecordEditForm('example.com.', data={
        'identifier': signed_record_data,
        **record_data,
    })
    assert not form.errors
    assert form.is_valid()
    mock_delete_record.assert_not_called()
    mock_create_record.assert_not_called()
    mock_update_record.assert_called_once_with(
        zone='example.com.',
        name='mail.example.com.',
        rtype='MX',
        old_content='0 example.org.',
        new_ttl=1337,
        new_content='0 example.org.',
    )


def test_recordeditform_change_content_only(mock_create_record, mock_delete_record, mock_update_record, record_data, signed_record_data):
    record_data['content'] = '100 example.org.'
    form = RecordEditForm('example.com.', data={
        'identifier': signed_record_data,
        **record_data,
    })
    assert not form.errors
    assert form.is_valid()
    mock_delete_record.assert_not_called()
    mock_create_record.assert_not_called()
    mock_update_record.assert_called_once_with(
        zone='example.com.',
        name='mail.example.com.',
        rtype='MX',
        old_content='0 example.org.',
        new_ttl=300,
        new_content='100 example.org.',
    )
