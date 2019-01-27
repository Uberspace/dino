from collections import namedtuple

import pytest
from django.core import signing
from django.shortcuts import reverse
from django.test import TestCase


@pytest.fixture
def signed_record_data():
    return signing.dumps({
        'zone': 'example.com.',
        'name': 'www.example.com.',
        'rtype': 'A',
        'content': '1.1.1.1',
    })

@pytest.mark.django_db()
def test_recorddeleteview_get(client_admin, mock_pdns_delete_record):
    response = client_admin.get(reverse('zoneeditor:zone_record_delete', kwargs={'zone': 'example.com.'}))
    assert response.status_code == 405
    mock_pdns_delete_record.assert_not_called()

@pytest.mark.django_db()
def test_recorddeleteview_post(client_admin, mock_pdns_delete_record, signed_record_data):
    response = client_admin.post(reverse('zoneeditor:zone_record_delete', kwargs={'zone': 'example.com.'}),
    data={
        'identifier': signed_record_data,
        'confirm': 'true',
    })
    TestCase().assertRedirects(response, '/zones/example.com./records', fetch_redirect_response=False)
    mock_pdns_delete_record.assert_called_once_with('example.com.', 'www.example.com.', 'A', '1.1.1.1')

@pytest.mark.django_db()
def test_recorddeleteview_post_no_confirm(client_admin, mock_pdns_delete_record, signed_record_data):
    response = client_admin.post(reverse('zoneeditor:zone_record_delete', kwargs={'zone': 'example.com.'}),
    data={
        'identifier': signed_record_data,
        'confirm': 'false',
    })
    TestCase().assertRedirects(response, '/zones/example.com./records', fetch_redirect_response=False)
    mock_pdns_delete_record.assert_not_called()

@pytest.mark.django_db()
def test_recorddeleteview_post_empty_confirm(client_admin, mock_pdns_delete_record, signed_record_data):
    response = client_admin.post(reverse('zoneeditor:zone_record_delete', kwargs={'zone': 'example.com.'}),
    data={
        'identifier': signed_record_data,
    })
    assert 'example.com' in response.content.decode()
    mock_pdns_delete_record.assert_not_called()
