import pytest
from django.shortcuts import reverse
from django.test import TestCase


@pytest.mark.django_db()
def test_recordeditview_get(client_admin):
    response = client_admin.get(reverse('zoneeditor:zone_record_edit', kwargs={'zone': 'example.com.'}))
    assert response.status_code == 405


@pytest.mark.django_db()
def test_recordeditview_get_unauthenicated(client):
    url = reverse('zoneeditor:zone_record_edit', kwargs={'zone': 'example.com.'})
    response = client.post(url)
    TestCase().assertRedirects(response, f'/accounts/login/?next={url}')


@pytest.mark.parametrize('client', [
    (pytest.lazy_fixture('client_admin')),
    (pytest.lazy_fixture('client_user_tenant_admin')),
])
@pytest.mark.django_db()
def test_recordeditview_post_granted(client, mock_create_record, mock_delete_record, signed_record_data):
    response = client.post(
        reverse('zoneeditor:zone_record_edit', kwargs={'zone': 'example.com.'}),
        data={'identifier': signed_record_data}
    )
    assert response.status_code == 200
    form = response.context_data['form']
    assert form['identifier'].value() == signed_record_data
    assert form['name'].value() == 'mail.example.com.'
    assert form['rtype'].value() == 'MX'
    assert form['ttl'].value() == 300
    assert form['content'].value() == '0 example.org.'
    mock_create_record.assert_not_called()
    mock_delete_record.assert_not_called()


@pytest.mark.django_db()
def test_recordeditview_post_submit(client_admin, mock_create_record, mock_delete_record, record_data, signed_record_data):
    record_data['rtype'] = 'AAAA'
    response = client_admin.post(
        reverse('zoneeditor:zone_record_edit', kwargs={'zone': 'example.com.'}),
        data={'identifier': signed_record_data, **record_data}
    )
    TestCase().assertRedirects(response, '/zones/example.com.', fetch_redirect_response=False)
    mock_delete_record.assert_called_once_with(
        zone='example.com.',
        name='mail.example.com.',
        rtype='MX',
        content='0 example.org.',
    )
    mock_create_record.assert_called_once_with(
        zone='example.com.',
        name='mail.example.com.',
        rtype='AAAA',
        ttl=300,
        content='0 example.org.',
    )


@pytest.mark.parametrize('client,zone_name', [
    (pytest.lazy_fixture('client_user_tenant_admin'), 'example.org.'),
    (pytest.lazy_fixture('client_user_tenant_user'), 'example.org.'),
])
@pytest.mark.django_db()
def test_recordeditview_post_denied(client, mock_create_record, mock_delete_record, zone_name, record_data, signed_record_data):
    record_data['content'] = '1 example.com.'
    response = client.post(
        reverse('zoneeditor:zone_record_edit', kwargs={'zone': zone_name}),
        data={'identifier': signed_record_data, **record_data}
    )
    assert response.status_code == 403
    mock_create_record.assert_not_called()
    mock_delete_record.assert_not_called()
