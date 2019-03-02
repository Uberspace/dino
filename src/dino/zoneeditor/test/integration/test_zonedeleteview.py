import pytest
from django.shortcuts import reverse
from django.test import TestCase
from dino.synczones.models import Zone


@pytest.mark.django_db()
def test_zonedeleteview_get(client_admin, mock_pdns_delete_zone):
    response = client_admin.get(reverse('zoneeditor:zone_delete'))
    assert response.status_code == 405
    mock_pdns_delete_zone.assert_not_called()


@pytest.mark.django_db()
def test_zonedeleteview_get_unauthenicated(client):
    url = reverse('zoneeditor:zone_delete')
    response = client.get(url)
    TestCase().assertRedirects(response, f'/accounts/login/?next={url}')


@pytest.mark.parametrize('client,zone_data', [
    (pytest.lazy_fixture('client_admin'), pytest.lazy_fixture('signed_example_com')),
    (pytest.lazy_fixture('client_user_tenant_admin'), pytest.lazy_fixture('signed_example_com')),
])
@pytest.mark.django_db()
def test_zonedeleteview_post_granted(client, mock_pdns_delete_zone, zone_data, db_zone):
    assert Zone.objects.filter(name='example.com.').exists()
    response = client.post(reverse('zoneeditor:zone_delete'), data={
        'identifier': zone_data,
        'confirm': 'true',
    })
    TestCase().assertRedirects(response, '/zones', fetch_redirect_response=False)
    mock_pdns_delete_zone.assert_called_once_with('example.com.')
    assert not Zone.objects.filter(name='example.com.').exists()


@pytest.mark.parametrize('client,zone_data', [
    (pytest.lazy_fixture('client_user_tenant_admin'), pytest.lazy_fixture('signed_example_org')),
    (pytest.lazy_fixture('client_user_tenant_user'), pytest.lazy_fixture('signed_example_org')),
    (pytest.lazy_fixture('client_user_tenant_user'), pytest.lazy_fixture('signed_example_com')),
])
@pytest.mark.django_db()
def test_zonedeleteview_post_denied(client, mock_pdns_delete_zone, zone_data):
    response = client.post(reverse('zoneeditor:zone_delete'), data={
        'identifier': zone_data,
        'confirm': 'true',
    })
    assert response.status_code == 403
    mock_pdns_delete_zone.assert_not_called()


@pytest.mark.django_db()
def test_zonedeleteview_post_unauthenicated(client):
    url = reverse('zoneeditor:zone_delete')
    response = client.post(url)
    TestCase().assertRedirects(response, f'/accounts/login/?next={url}')


@pytest.mark.django_db()
def test_zonedeleteview_post_no_confirm(client_admin, mock_pdns_delete_zone, signed_example_com):
    response = client_admin.post(reverse('zoneeditor:zone_delete'), data={
        'identifier': signed_example_com,
        'confirm': 'false',
    })
    TestCase().assertRedirects(response, '/zones', fetch_redirect_response=False)
    mock_pdns_delete_zone.assert_not_called()


@pytest.mark.django_db()
def test_zonedeleteview_post_empty_confirm(client_admin, mock_pdns_delete_zone, signed_example_com):
    response = client_admin.post(reverse('zoneeditor:zone_delete'), data={
        'identifier': signed_example_com,
    })
    assert 'example.com.' in response.content.decode()
    mock_pdns_delete_zone.assert_not_called()


@pytest.mark.django_db()
def test_zonedeleteview_post_unknown_zone(client_admin, mocker, signed_example_com):
    from dino.pdns_api import PDNSError
    mocker.patch('dino.pdns_api.pdns.delete_zone', side_effect=PDNSError('/', 422, 'Could not find domain'))
    response = client_admin.post(reverse('zoneeditor:zone_delete'), data={
        'identifier': signed_example_com,
        'confirm': 'true',
    })
    content = response.content.decode()
    assert response.status_code != 302
    assert 'Could not find domain' in content
