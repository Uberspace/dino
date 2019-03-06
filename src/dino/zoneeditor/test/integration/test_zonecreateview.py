import pytest
from django.shortcuts import reverse
from django.test import TestCase


@pytest.mark.django_db()
def test_zonecreateview_get(client_admin, mock_create_zone):
    response = client_admin.get(reverse('zoneeditor:zone_create'))
    assert response.status_code == 200


@pytest.mark.django_db()
def test_zonecreateview_get_unauthenicated(client):
    url = reverse('zoneeditor:zone_create')
    response = client.get(url)
    TestCase().assertRedirects(response, f'/accounts/login/?next={url}')


@pytest.mark.parametrize('client,zone_name', [
    (pytest.lazy_fixture('client_admin'), 'example.co.uk.'),
    (pytest.lazy_fixture('client_user_tenant_admin'), 'example.co.uk.'),
])
@pytest.mark.django_db()
def test_zonecreateview_post_granted(client, tenant, mock_create_zone, zone_name):
    response = client.post(reverse('zoneeditor:zone_create'), data={
        'name': zone_name,
        'tenants': tenant.pk,
    })
    TestCase().assertRedirects(response, '/zones/example.co.uk.', target_status_code=302)
    mock_create_zone.assert_called_with(kind='Native', name='example.co.uk.', nameservers=[])


@pytest.mark.parametrize('client,zone_name', [
    (pytest.lazy_fixture('client_user_tenant_user'), 'example.co.uk.'),
])
@pytest.mark.django_db()
def test_zonecreateview_post_denied(client, mock_create_zone, zone_name):
    response = client.post(reverse('zoneeditor:zone_create'), data={
        'name': zone_name,
    })
    assert response.status_code == 403
    mock_create_zone.assert_not_called()


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
    response = client.post(url)
    TestCase().assertRedirects(response, f'/accounts/login/?next={url}')
