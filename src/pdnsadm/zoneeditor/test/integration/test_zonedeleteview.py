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
