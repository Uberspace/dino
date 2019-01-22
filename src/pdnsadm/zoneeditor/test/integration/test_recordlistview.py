from collections import namedtuple

import pytest
from django.shortcuts import reverse
from django.test import TestCase


@pytest.fixture
def mock_pdns_get_records(mocker):
    rval = [
        {'name': r[0], 'ttl': r[1], 'rtype': r[2], 'content': r[3]}
        for r in [
            ('mail.example.com', 300, 'A', '1.2.3.4'),
            ('example.com', 300, 'MX', '0 mail.example.org'),
        ]
    ]
    return mocker.patch('pdnsadm.pdns_api.pdns.get_records', return_value=rval)

@pytest.mark.django_db()
def test_recordlistview(client_admin, mock_pdns_get_records):
    response = client_admin.get(reverse('zoneeditor:zone_records', kwargs={'zone': 'example.com'}))
    content = response.content.decode()
    assert response.status_code == 200
    assert 'mail.example.com' in content
    assert 'example.com' in content
    assert 'mail.example.org' in content

@pytest.mark.django_db()
def test_recordlistview_unauthenicated(client):
    url = reverse('zoneeditor:zone_records', kwargs={'zone': 'example.com'})
    response = client.get(url)
    TestCase().assertRedirects(response, f'/accounts/login/?next={url}')
