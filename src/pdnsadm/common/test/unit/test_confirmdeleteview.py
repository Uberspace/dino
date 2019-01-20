from django import forms
from django.test import RequestFactory
from django.views.generic.base import TemplateView

from ...views import DeleteConfirmView
import pytest

class T(DeleteConfirmView):
    redirect_url = '/success'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

@pytest.fixture
def get_view():
    def inner(kwargs, request=RequestFactory().get('/')):
        c = T()
        c.kwargs = kwargs
        c.request = request
        return c
    return inner

def test_deleteconfirmview_missing_pk():
    with pytest.raises(Exception) as excinfo:
        T.as_view()(RequestFactory().get('/'))

    assert 'expected request' in str(excinfo)

def test_deleteconfirmview_get(mocker, get_view, mock_delete_entity, mock_messages_success):
    c = get_view({'pk': 'asd'})
    response = c.get(c.request)
    response.render()
    assert not c.confirmed
    assert c.identifier == 'asd'
    mock_delete_entity.assert_not_called()
    mock_messages_success.assert_not_called()
    assert response.status_code == 200
    assert 'asd' in str(response.content)

def test_deleteconfirmview_post_canceled(mocker, get_view, mock_delete_entity, mock_messages_success):
    c = get_view({'pk': 'asd'}, RequestFactory().post('/', data={'confirm': 'false'}))
    response = c.post()
    assert not c.confirmed
    mock_delete_entity.assert_not_called()
    mock_messages_success.assert_not_called()
    assert response.status_code == 302
    assert response['Location'] == '/success'

def test_deleteconfirmview_post_confirmed(mocker, get_view, mock_delete_entity, mock_messages_success):
    c = get_view({'pk': 'asd'}, RequestFactory().post('/', data={'confirm': 'true'}))
    response = c.post()
    assert c.confirmed
    mock_delete_entity.assert_called_once_with('asd')
    mock_messages_success.assert_called_once_with(c.request, 'asd has been deleted.')
    assert response.status_code == 302
    assert response['Location'] == '/success'
