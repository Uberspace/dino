import pytest
from django.shortcuts import reverse
from django.test import TestCase


@pytest.fixture
def mock_pdns_get_records(mocker):
    rval = [
        {'name': r[0], 'ttl': r[1], 'rtype': r[2], 'content': r[3]}
        for r in [
            ('mail.example.com.', 300, 'A', '1.2.3.4'),
            ('example.com.', 300, 'MX', '0 mail.example.org.'),
        ]
    ]
    return mocker.patch('dino.pdns_api.pdns.get_records', return_value=rval)


@pytest.mark.parametrize('client', [
    (pytest.lazy_fixture('client_admin')),
    (pytest.lazy_fixture('client_user_tenant_admin')),
    (pytest.lazy_fixture('client_user_tenant_user')),
])
@pytest.mark.django_db()
def test_recordlistview(client, mock_pdns_get_records):
    response = client.get(reverse('zoneeditor:zone_records', kwargs={'zone': 'example.com.'}))
    content = response.content.decode()
    assert response.status_code == 200
    assert 'mail.example.com.' in content
    assert 'example.com.' in content
    assert 'mail.example.org.' in content


@pytest.mark.parametrize('client', [
    (pytest.lazy_fixture('client_user_tenant_admin')),
    (pytest.lazy_fixture('client_user_tenant_user')),
])
@pytest.mark.django_db()
def test_recordlistview_denied(client, mock_pdns_get_records):
    response = client.post(reverse('zoneeditor:zone_records', kwargs={'zone': 'example.org.'}))
    assert response.status_code == 403


@pytest.mark.django_db()
def test_recordlistview_404(client_admin, mocker):
    from dino.pdns_api import PDNSNotFoundException
    mocker.patch('dino.pdns_api.pdns.get_records', side_effect=PDNSNotFoundException)
    response = client_admin.get(reverse('zoneeditor:zone_records', kwargs={'zone': 'example.com.'}))
    assert response.status_code == 404


@pytest.mark.django_db()
def test_recordlistview_unauthenicated(client):
    url = reverse('zoneeditor:zone_records', kwargs={'zone': 'example.com.'})
    response = client.get(url)
    TestCase().assertRedirects(response, f'/accounts/login/?next={url}')


@pytest.mark.django_db()
def test_recordlistview_user_tenant_admin(client_user_tenant_admin, mock_pdns_get_zones, mock_pdns_get_records):
    response = client_user_tenant_admin.get(reverse('zoneeditor:zone_records', kwargs={'zone': 'example.com.'}))
    content = response.content.decode()
    assert response.status_code == 200
    assert 'mail.example.com.' in content
    assert 'example.com.' in content
    assert 'mail.example.org.' in content


@pytest.mark.django_db()
def test_recordlistview_user_no_tenant(client_user_no_tenant, db_zone, mock_pdns_get_zones, mock_pdns_get_records):
    response = client_user_no_tenant.get(reverse('zoneeditor:zone_records', kwargs={'zone': 'example.com.'}))
    response.content.decode()
    assert response.status_code == 403
