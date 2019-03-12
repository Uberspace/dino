import django.forms as forms
import pytest
from allauth.exceptions import ImmediateHttpResponse
from django.contrib.auth import get_user_model
from django.test import RequestFactory
from django.test.utils import override_settings

from ...allauth import DinoAccountAdapter, DinoSocialAccountAdapter, _check_email_domain


def test_accountadapter_signup():
    adapter = DinoAccountAdapter()
    request = RequestFactory().get('/')

    assert adapter.is_open_for_signup(request) is False

    with override_settings(ENABLE_EMAIL_SIGNUP=False):
        assert adapter.is_open_for_signup(request) is False

    with override_settings(ENABLE_SOCIAL_SIGNUP=True):
        assert adapter.is_open_for_signup(request) is False

    with override_settings(ENABLE_EMAIL_SIGNUP=True):
        assert adapter.is_open_for_signup(request) is True


def test_socialaccountadapter_signup():
    adapter = DinoSocialAccountAdapter()
    request = RequestFactory().get('/')

    assert adapter.is_open_for_signup(request) is False

    with override_settings(ENABLE_SOCIAL_SIGNUP=False):
        assert adapter.is_open_for_signup(request) is False

    with override_settings(ENABLE_EMAIL_SIGNUP=True):
        assert adapter.is_open_for_signup(request) is False

    with override_settings(ENABLE_SOCIAL_SIGNUP=True):
        assert adapter.is_open_for_signup(request) is True


def test_accountadapter_email():
    adpater = DinoAccountAdapter()

    assert adpater.clean_email('some@example.com')

    with override_settings(VALID_SIGNUP_DOMAINS=['example.com', 'example.de']):
        adpater.clean_email('some@example.com')
        adpater.clean_email('some@example.de')

        with pytest.raises(forms.ValidationError):
            adpater.clean_email('some@example.org')


class FakeSocialLogin():
    def __init__(self, email):
        self.email = email

    @property
    def user(self):
        return get_user_model()(
            email=self.email
        )


def test_accountadapter_pre_social_login():
    adpater = DinoSocialAccountAdapter()

    adpater.pre_social_login(None, FakeSocialLogin('some@example.com'))

    with override_settings(VALID_SIGNUP_DOMAINS=['example.com', 'example.de']):
        adpater.pre_social_login(None, FakeSocialLogin('some@example.com'))
        adpater.pre_social_login(None, FakeSocialLogin('some@example.de'))

        with pytest.raises(ImmediateHttpResponse):
            adpater.pre_social_login(None, FakeSocialLogin('some@example.org'))


def test_accountadapter_check_email():
    with pytest.raises(forms.ValidationError):
        _check_email_domain('to@many@at.signs')
