import pytest
from django.shortcuts import reverse
from django.test import TestCase


@pytest.mark.django_db()
def test_zonelistview(client_admin, mock_pdns_get_zones):
    response = client_admin.get(reverse('zoneeditor:zone_list'))
    content = response.content.decode()
    assert response.status_code == 200
    assert 'example.com.' in content
    assert 'example.org.' in content
    assert 'example16.org' in content
    assert 'example400.org' not in content

@pytest.mark.django_db()
def test_zonelistview_filter(client_admin, mock_pdns_get_zones):
    response = client_admin.get(reverse('zoneeditor:zone_list') + '?q=example.org.')
    content = response.content.decode()
    assert response.status_code == 200
    assert len(response.context['objects']) == 1
    assert response.context['objects'][0].name == 'example.org.'

@pytest.mark.django_db()
def test_zonelistview_unauthenicated(client):
    url = reverse('zoneeditor:zone_list')
    response = client.get(url)
    TestCase().assertRedirects(response, f'/accounts/login/?next={url}')

@pytest.mark.django_db()
def test_zonelistview_user_tenant(client_user_tenant, mock_pdns_get_zones):
    response = client_user_tenant.get(reverse('zoneeditor:zone_list'))
    content = response.content.decode()
    assert response.status_code == 200
    assert 'example.com.' in content
    assert 'example.org.' not in content
    assert 'example16.org' not in content

@pytest.mark.django_db()
def test_zonelistview_user_no_tenant(client_user_no_tenant, mock_pdns_get_zones):
    response = client_user_no_tenant.get(reverse('zoneeditor:zone_list'))
    content = response.content.decode()
    assert response.status_code == 200
    assert 'example.com.' not in content
    assert 'example.org.' not in content
    assert 'example16.org' not in content
