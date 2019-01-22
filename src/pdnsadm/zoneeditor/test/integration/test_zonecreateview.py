from collections import namedtuple

import pytest
from django.shortcuts import reverse
from django.test import TestCase


@pytest.mark.django_db()
def test_zonecreateview_get(client_admin, mock_create_zone):
    response = client_admin.get(reverse('zoneeditor:zone_create'))
    assert response.status_code == 200

@pytest.mark.django_db()
def test_zonecreateview_post(client_admin, mock_create_zone):
    response = client_admin.post(reverse('zoneeditor:zone_create'), data={
        'name': 'example.com'
    })
    TestCase().assertRedirects(response, '/zones/example.com.', target_status_code=302)
    mock_create_zone.assert_called_with(kind='Native', name='example.com.', nameservers=[])

@pytest.mark.django_db()
def test_zonecreateview_post_empty(client_admin, mock_create_zone):
    response = client_admin.post(reverse('zoneeditor:zone_create'))
    assert response.status_code == 200
    content = response.content.decode()
    assert 'is required' in content
    mock_create_zone.assert_not_called()

@pytest.mark.django_db()
def test_zonecreateview_post_unauthenicated(client):
    url = reverse('zoneeditor:zone_create')
    response = client.get(url)
    TestCase().assertRedirects(response, f'/accounts/login/?next={url}')
