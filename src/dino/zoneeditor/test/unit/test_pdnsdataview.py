from django import forms
from django.test import RequestFactory
from django.views.generic.base import TemplateView

from ...views import PDNSDataView


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
    assert data['objects'][0] == 0
    assert data['objects'][-1] == 18


def test_pdnsdataview_limit_objects():
    class C(T):
        def get_objects(self):
            return range(500)

    data = C().get_context_data()

    assert len(data['objects']) == 20
    assert data['objects'][0] == 0
    assert data['objects'][-1] == 19


def test_pdnsdataview_paginate_by():
    class C(T):
        paginate_by = 5

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
    assert list(data['objects']) == [{'content': '0.0.0.0', 'name': 'something.domain.com.'}]

    c.filter_properties = ['name', 'content']
    data = c.get_context_data()
    assert len(data['objects']) == 2
    assert list(data['objects']) == [{'content': '0.0.0.0', 'name': 'something.domain.com.'}, {'content': 'something.else.domain.com.', 'name': ''}]


def test_pdnsdataview_search_case():
    class C(T):
        _request = '/?q=SOMEthing'

        def get_objects(self):
            return [
                {'name': 'something.domain.com.', 'content': '0.0.0.0'},
            ]

    c = C()

    c.filter_properties = ['name']
    data = c.get_context_data()
    assert len(data['objects']) == 1
    assert list(data['objects']) == [{'content': '0.0.0.0', 'name': 'something.domain.com.'}]


def test_pdnsdataview_page():
    class C(T):
        _request = '/?page=2'

        def get_objects(self):
            return range(500)

    c = C()

    c.filter_properties = ['name']
    data = c.get_context_data()
    assert len(data['objects']) == 20
    assert data['objects'][-1] == 39


def test_pdnsdataview_search_object():
    class C(T):
        _request = '/?q=something'

        def get_objects(self):
            return [
                type('Record', (object,), {'name': 'something.domain.com', 'content': 'aaa'})()
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
