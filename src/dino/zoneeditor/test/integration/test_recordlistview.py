import math

import pytest
from bs4 import BeautifulSoup
from django.shortcuts import reverse
from django.test import TestCase


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


@pytest.mark.django_db()
def test_recordlistview_pagination_controls_first(client_admin, db_zone, mock_pdns_get_zones, mock_pdns_get_records):
    url = reverse('zoneeditor:zone_records', kwargs={'zone': 'example.com.'})
    response = client_admin.get(url + '?q=example')
    content = response.content.decode()
    soup = BeautifulSoup(content, 'html.parser')

    previous_page = soup.select('.pagination li:first-child')[0]
    assert 'disabled' in previous_page['class']

    next_page = soup.select('.pagination li:last-child')[0]
    next_page_url = next_page.select('a')[0]['href']
    assert 'q=example' in next_page_url
    assert 'disabled' not in next_page.get('class', '')

    first_num = soup.select('.pagination li:nth-child(3)')[0]
    assert first_num.select('a')[0]['href'] == next_page_url

    response = client_admin.get(url + next_page_url)
    assert response.status_code == 200


@pytest.mark.django_db()
def test_recordlistview_pagination_controls_last(client_admin, db_zone, mock_pdns_get_zones, mock_pdns_get_records):
    url = reverse('zoneeditor:zone_records', kwargs={'zone': 'example.com.'})
    pages = math.ceil(len(mock_pdns_get_records())/20)
    response = client_admin.get(f'{url}?q=example&page={pages}')
    content = response.content.decode()
    soup = BeautifulSoup(content, 'html.parser')

    previous_page = soup.select('.pagination li:first-child')[0]
    previous_page_url = url + previous_page.select('a')[0]['href']
    assert 'q=example' in previous_page_url
    assert 'disabled' not in previous_page.get('class', '')

    response = client_admin.get(previous_page_url)
    assert response.status_code == 200

    next_page = soup.select('.pagination li:last-child')[0]
    assert 'disabled' in next_page['class']


@pytest.mark.django_db()
def test_recordlistview_buttons(client_admin, db_zone, mock_pdns_get_zones, mock_pdns_get_records):
    response = client_admin.get(reverse('zoneeditor:zone_records', kwargs={'zone': 'example.com.'}))
    content = response.content.decode()
    soup = BeautifulSoup(content, 'html.parser')

    edit_btns = soup.select('table tbody tr td .edit')
    assert len(edit_btns) == 20

    delete_btns = soup.select('table tbody tr td .delete')
    assert len(delete_btns) == 20


@pytest.mark.django_db()
def test_recordlistview_buttons_delete_soa(client_admin, db_zone, mock_pdns_get_zones, mock_pdns_get_records):
    response = client_admin.get(reverse('zoneeditor:zone_records', kwargs={'zone': 'example.com.'}) + '?q=SOA')
    content = response.content.decode()

    assert 'a.misconfigured.powerdns.server.' in content

    soup = BeautifulSoup(content, 'html.parser')

    delete_btns = soup.select('table tbody tr')
    assert len(delete_btns) > 0

    delete_btns = soup.select('table tbody tr td .delete')
    assert len(delete_btns) == 0


@pytest.mark.django_db()
def test_recordlistview_pagination(client_admin, mock_pdns_get_records):
    response = client_admin.get(reverse('zoneeditor:zone_records', kwargs={'zone': 'example.com.'}))
    assert len(response.context_data['object_list']) == 20
    assert response.context_data['object_list'][0]['name'] == 'mail.example.com.'
    assert response.context_data['object_list'][-1]['name'] == 'r17.example.com.'


@pytest.mark.django_db()
def test_recordlistview_pagination_page(client_admin, mock_pdns_get_records):
    response = client_admin.get(reverse('zoneeditor:zone_records', kwargs={'zone': 'example.com.'}) + '?page=5')
    assert len(response.context_data['object_list']) == 20
    assert response.context_data['object_list'][0]['name'] == 'r78.example.com.'
    assert response.context_data['object_list'][-1]['name'] == 'r97.example.com.'


@pytest.mark.parametrize('q,count,name', [
    ('r170', 1, 'r170.example.com.'),
    ('R170', 1, 'r170.example.com.'),
    ('%40', 1, 'example.com.'),
])
@pytest.mark.django_db()
def test_recordlistview_search_name(client_admin, mock_pdns_get_records, q, count, name):
    response = client_admin.get(reverse('zoneeditor:zone_records', kwargs={'zone': 'example.com.'}) + f'?q={q}')
    assert len(response.context_data['object_list']) == count
    assert response.context_data['object_list'][0]['name'] == name


@pytest.mark.django_db()
def test_recordlistview_search_rtype(client_admin, mock_pdns_get_records):
    response = client_admin.get(reverse('zoneeditor:zone_records', kwargs={'zone': 'example.com.'}) + '?q=MX')
    assert len(response.context_data['object_list']) == 1
    assert response.context_data['object_list'][0]['name'] == 'example.com.'


@pytest.mark.django_db()
def test_recordlistview_search_echo(client_admin, mock_pdns_get_records):
    response = client_admin.get(reverse('zoneeditor:zone_records', kwargs={'zone': 'example.com.'}) + '?q=MX')
    assert response.context_data['search_form'].initial['q'] == 'MX'


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
