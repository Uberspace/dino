from collections import namedtuple

import pytest
from django.shortcuts import reverse
from django.test import TestCase


@pytest.mark.django_db()
def test_recordcreateview_get(client_admin, mock_create_record):
    response = client_admin.get(reverse('zoneeditor:zone_record_create', kwargs={'zone': 'example.com.'}))
    assert response.status_code == 200
    mock_create_record.assert_not_called()

@pytest.mark.django_db()
def test_recordcreateview_get_unauthenicated(client):
    url = reverse('zoneeditor:zone_record_create', kwargs={'zone': 'example.com.'})
    response = client.get(url)
    TestCase().assertRedirects(response, f'/accounts/login/?next={url}')

@pytest.mark.django_db()
def test_recordcreateview_post(client_admin, mock_create_record):
    response = client_admin.post(reverse('zoneeditor:zone_record_create', kwargs={'zone': 'example.com.'}), data={
        'zone': 'example.com.',
        'name': 'mail.anexample.com.example.com.',
        'rtype': 'MX',
        'ttl': 300,
        'content': '0 example.org.',
    })
    TestCase().assertRedirects(response, '/zones/example.com.', fetch_redirect_response=False)
    mock_create_record.assert_called_once_with(
        zone='example.com.',
        name='mail.anexample.com.example.com.',
        rtype='MX',
        ttl=300,
        content='0 example.org.',
    )

@pytest.mark.django_db()
def test_recordcreateview_post_unauthenicated(client):
    url = reverse('zoneeditor:zone_record_create', kwargs={'zone': 'example.com.'})
    response = client.post(url)
    TestCase().assertRedirects(response, f'/accounts/login/?next={url}')
