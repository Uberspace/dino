import pytest
from django import forms
from django.test import RequestFactory
from django.views.generic.base import TemplateView

from .views import PDNSDataView, ZoneCreateForm


class T(PDNSDataView, TemplateView):
    _request = '/'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.request = RequestFactory().get(self._request)

def test_pdnsdataview():
    class C(T):
        def get_objects(self):
            return range(19)

    data = C().get_context_data()

    assert len(data['objects']) == 19
    assert data['count_all'] == 19
    assert data['count_shown'] == 19
    assert data['objects'][0] == 0
    assert data['objects'][-1] == 18

def test_pdnsdataview_limit_objects():
    class C(T):
        def get_objects(self):
            return range(500)

    data = C().get_context_data()

    assert len(data['objects']) == 20
    assert data['count_all'] == 500
    assert data['count_shown'] == 20
    assert data['objects'][0] == 0
    assert data['objects'][-1] == 19

def test_pdnsdataview_max_objects():
    class C(T):
        max_objects = 5

        def get_objects(self):
            return range(500)

    data = C().get_context_data()

    assert len(data['objects']) == 5

def test_pdnsdataview_search():
    class C(T):
        _request = '/?q=something'

        def get_objects(self):
            return [
                {'name': 'something.domain.com.', 'content': '0.0.0.0'},
                {'name': '', 'content': 'something.else.domain.com.'},
            ]

    c = C()

    c.filter_properties = ['name']
    data = c.get_context_data()
    assert len(data['objects']) == 1
    assert data['objects'] == [{'content': '0.0.0.0', 'name': 'something.domain.com.'}]

    c.filter_properties = ['name', 'content']
    data = c.get_context_data()
    assert len(data['objects']) == 2
    assert data['objects'] == [{'content': '0.0.0.0', 'name': 'something.domain.com.'}, {'content': 'something.else.domain.com.', 'name': ''}]


def test_pdnsdataview_search_object():
    class C(T):
        _request = '/?q=something'

        def get_objects(self):
            return [
                type('Record', (object,), {'name':'something.domain.com', 'content': 'aaa'})()
            ]

    c = C()

    c.filter_properties = ['name']
    data = c.get_context_data()
    assert len(data['objects']) == 1
    assert data['objects'][0].name == 'something.domain.com'

    c.filter_properties = ['content']
    data = c.get_context_data()
    assert len(data['objects']) == 0

def test_pdnsdataview_search_echo():
    class C(T):
        _request = '/?q=something'

        def get_objects(self):
            return []

    data = C().get_context_data()
    assert isinstance(data['search_form'], forms.Form)
    assert data['search_form'].initial['q'] == 'something'

@pytest.fixture
def mock_create_zone(mocker):
    return mocker.patch('pdnsadm.pdns_api.pdns.create_zone')

def test_zonecreateform(mock_create_zone):
    form = ZoneCreateForm(data={'name': 'example.com.'})
    assert form.is_valid()
    mock_create_zone.assert_called_once_with(name='example.com.', kind='Native', nameservers=[])

def test_zonecreateform_name_add_dot(mock_create_zone):
    form = ZoneCreateForm(data={'name': 'example.com'})
    assert form.is_valid()
    mock_create_zone.assert_called_once_with(name='example.com.', kind='Native', nameservers=[])

def test_zonecreateform_invalid_no_creation(mock_create_zone):
    form = ZoneCreateForm({'name': 'blargh--'})
    form.full_clean()
    mock_create_zone.assert_not_called()

def test_zonecreateform_api_error(mocker):
    from pdnsadm.pdns_api import PDNSError
    m = mocker.patch('pdnsadm.pdns_api.pdns.create_zone', side_effect=PDNSError('/', 400, 'broken'))
    form = ZoneCreateForm({'name': 'domain.com.'})
    form.full_clean()
    assert 'broken' in form.errors['__all__'][0]
    m.assert_called_once()

def test_zonecreateform_name_required(mock_create_zone):
    form = ZoneCreateForm({})
    form.full_clean()
    assert 'required' in form.errors['name'][0]

def test_zonecreateform_name_invalid(mock_create_zone):
    form = ZoneCreateForm({'name': 'hostname'})
    assert not form.is_valid()
