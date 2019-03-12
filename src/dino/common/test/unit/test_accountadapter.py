from django.test import RequestFactory
from django.test.utils import override_settings

from ...allauth import NoNewUsersAccountAdapter


def test_accountadapter_signup():
    adapter = NoNewUsersAccountAdapter()
    request = RequestFactory().get('/')

    assert adapter.is_open_for_signup(request) is False

    with override_settings(ENABLE_SIGNUP=False):
        assert adapter.is_open_for_signup(request) is False

    with override_settings(ENABLE_SIGNUP=True):
        assert adapter.is_open_for_signup(request) is True
