from collections import namedtuple

import pytest
from django.shortcuts import reverse
from django.test import TestCase


@pytest.mark.django_db()
def test_zonedeleteview_get(client_admin, mock_pdns_delete_zone):
    response = client_admin.get(reverse('zoneeditor:zone_delete'))
    assert response.status_code == 405
    mock_pdns_delete_zone.assert_not_called()

@pytest.mark.django_db()
def test_zonedeleteview_post(client_admin, mock_pdns_delete_zone):
    response = client_admin.post(reverse('zoneeditor:zone_delete'), data={
        'identifier': 'some.zone.',
        'confirm': 'true',
    })
    TestCase().assertRedirects(response, '/zones')
    mock_pdns_delete_zone.assert_called_once_with('some.zone.')

@pytest.mark.django_db()
def test_zonedeleteview_post_unknown_zone(client_admin, mocker):
    from pdnsadm.pdns_api import PDNSError
    m = mocker.patch('pdnsadm.pdns_api.pdns.delete_zone', side_effect=PDNSError('/', 422, 'Could not find domain'))
    response = client_admin.post(reverse('zoneeditor:zone_delete'), data={
        'identifier': 'some.zone.',
        'confirm': 'true',
    })
    content = response.content.decode()
    assert response.status_code != 302
    assert 'Could not find domain' in content
