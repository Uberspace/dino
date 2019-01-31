from collections import namedtuple

import pytest
from django.core import signing
from django.shortcuts import reverse
from django.test import TestCase


@pytest.fixture
def signed_record_data_example_com():
    return signing.dumps({
        'zone': 'example.com.',
        'name': 'www.example.com.',
        'rtype': 'A',
        'content': '1.1.1.1',
    })

@pytest.fixture
def signed_record_data_example_org():
    return signing.dumps({
        'zone': 'example.org.',
        'name': 'www.example.org.',
        'rtype': 'A',
        'content': '1.1.1.1',
    })

@pytest.mark.django_db()
def test_recorddeleteview_get(client_admin, mock_pdns_delete_record):
    response = client_admin.get(reverse('zoneeditor:zone_record_delete', kwargs={'zone': 'example.com.'}))
    assert response.status_code == 405
    mock_pdns_delete_record.assert_not_called()

@pytest.mark.django_db()
def test_recorddeleteview_get_unauthenicated(client):
    url = reverse('zoneeditor:zone_record_delete', kwargs={'zone': 'example.com.'})
    response = client.get(url)
    TestCase().assertRedirects(response, f'/accounts/login/?next={url}')

@pytest.mark.django_db()
def test_recorddeleteview_post(client_admin, mock_pdns_delete_record, signed_record_data_example_com):
    response = client_admin.post(reverse('zoneeditor:zone_record_delete', kwargs={'zone': 'example.com.'}),
    data={
        'identifier': signed_record_data_example_com,
        'confirm': 'true',
    })
    TestCase().assertRedirects(response, '/zones/example.com./records', fetch_redirect_response=False)
    mock_pdns_delete_record.assert_called_once_with('example.com.', 'www.example.com.', 'A', '1.1.1.1')

@pytest.mark.django_db()
def test_recorddeleteview_name_missmatch(client_user_tenant_admin, mock_pdns_delete_record, signed_record_data_example_org):
    response = client_user_tenant_admin.post(reverse('zoneeditor:zone_record_delete', kwargs={'zone': 'example.com.'}),
    data={
        'identifier': signed_record_data_example_org,
        'confirm': 'true',
    })
    assert response.status_code == 400
    mock_pdns_delete_record.assert_not_called()

@pytest.mark.django_db()
def test_recorddeleteview_post_unauthenicated(client):
    url = reverse('zoneeditor:zone_record_delete', kwargs={'zone': 'example.com.'})
    response = client.post(url)
    TestCase().assertRedirects(response, f'/accounts/login/?next={url}')

@pytest.mark.django_db()
def test_recorddeleteview_post_no_confirm(client_admin, mock_pdns_delete_record, signed_record_data_example_com):
    response = client_admin.post(reverse('zoneeditor:zone_record_delete', kwargs={'zone': 'example.com.'}),
    data={
        'identifier': signed_record_data_example_com,
        'confirm': 'false',
    })
    TestCase().assertRedirects(response, '/zones/example.com./records', fetch_redirect_response=False)
    mock_pdns_delete_record.assert_not_called()

@pytest.mark.django_db()
def test_recorddeleteview_post_empty_confirm(client_admin, mock_pdns_delete_record, signed_record_data_example_com):
    response = client_admin.post(reverse('zoneeditor:zone_record_delete', kwargs={'zone': 'example.com.'}),
    data={
        'identifier': signed_record_data_example_com,
    })
    assert 'example.com.' in response.content.decode()
    mock_pdns_delete_record.assert_not_called()
