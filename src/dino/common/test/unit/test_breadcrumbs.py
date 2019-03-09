from django.test import RequestFactory

import dino.common.context_processors as cp


def test_breadcrumbs_list_urls():
    urls = cp.list_urls()
    assert len(urls) > 20
    assert 'zones/<zonename:zone>/records' in urls


def test_breadcrumbs_assemble():
    assert cp.assemble(['//profile', '', '^/$', 'foo//^']) == 'profile/foo/^'


def test_breadcrumbs_parent_urls():
    assert cp.get_parent_urls('/zones/zone.com./records') == [
        'zones',
        'zones/<zonename:zone>',
        'zones/<zonename:zone>/records',
    ]


def test_breadcrumbs_get_breadcrumbs():
    crumbs = list(cp.get_breadcrumbs('/zones/foo.com./records'))
    assert crumbs == [
        {'crumb': 'zones', 'url': '/zones'},
        {'crumb': 'foo.com.', 'url': '/zones/foo.com.'},
        {'crumb': 'records', 'url': '/zones/foo.com./records'}
    ]


def test_breadcrumbs_get_breadcrumbs_split():
    crumbs = list(cp.get_breadcrumbs('/accounts/login/'))
    assert crumbs == [
        {'crumb': 'accounts', 'url': None},
        {'crumb': 'login', 'url': '/accounts/login'},
    ]


def test_breadcrumbs_breadcrumbs():
    request = RequestFactory().get('/zones/foo.com./records')
    rtn = cp.breadcrumbs(request)
    assert rtn['breadcrumbs'] == [
        {'crumb': 'zones', 'url': '/zones'},
        {'crumb': 'foo.com.', 'url': '/zones/foo.com.'},
        {'crumb': 'records', 'url': '/zones/foo.com./records'}
    ]
