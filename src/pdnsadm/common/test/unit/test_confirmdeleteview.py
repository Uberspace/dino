from django import forms
from django.test import RequestFactory
from django.views.generic.base import TemplateView

from ...views import DeleteConfirmView
import pytest

class T(DeleteConfirmView):
    redirect_url = '/success'

def test_deleteconfirmview_get():
    response = T.as_view()(RequestFactory().get('/'))
    assert response.status_code == 405

def test_deleteconfirmview_post_empty():
    with pytest.raises(Exception) as excinfo:
        T.as_view()(RequestFactory().post('/'))

    assert 'expected request to have POST field' in str(excinfo)

def test_deleteconfirmview_post_invalid():
    with pytest.raises(Exception) as excinfo:
        T.as_view()(RequestFactory().post('/', data={'someinvalidfield': 'whatisthis'}))

    assert 'expected request to have POST field' in str(excinfo)
    assert 'someinvalidfield' in str(excinfo)

def test_deleteconfirmview_post_first(mocker, mock_delete_entity, mock_messages_success):
    c = T()
    response = c.post(RequestFactory().post('/', data={'identifier': 'asd'}))
    assert c.confirmed is None
    assert c.identifier == 'asd'
    mock_delete_entity.assert_not_called()
    mock_messages_success.assert_not_called()
    assert response.status_code == 200

def test_deleteconfirmview_post_canceled(mocker, mock_delete_entity, mock_messages_success):
    c = T()
    response = c.post(RequestFactory().post('/', data={'confirm': 'false', 'identifier': ''}))
    assert c.confirmed is False
    assert c.identifier == ''
    mock_delete_entity.assert_not_called()
    mock_messages_success.assert_not_called()
    assert response.status_code == 302
    assert response['Location'] == '/success'

def test_deleteconfirmview_post_confirmed(mocker, mock_delete_entity, mock_messages_success):
    c = T()
    response = c.post(RequestFactory().post('/', data={'confirm': 'true', 'identifier': 'asd'}))
    assert c.confirmed is True
    assert c.identifier == 'asd'
    mock_delete_entity.assert_called_once_with('asd')
    mock_messages_success.assert_called_once_with(c.request, 'asd has been deleted.')
    assert response.status_code == 302
    assert response['Location'] == '/success'

def test_deleteconfirmview_post_error(mocker, mock_messages_success, mock_messages_error):
    from pdnsadm.pdns_api import PDNSError
    delete_entity = mocker.patch('pdnsadm.common.views.DeleteConfirmView.delete_entity', side_effect=PDNSError('/', 400, 'something broke'))
    c = T()
    response = c.post(RequestFactory().post('/', data={'confirm': 'true', 'identifier': 'asd'}))
    assert response.status_code != 302
    mock_messages_success.assert_not_called()
    mock_messages_error.assert_called_once_with(c.request, 'PowerDNS error: something broke')
