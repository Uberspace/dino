import django.forms as forms
from allauth.account.adapter import DefaultAccountAdapter
from allauth.exceptions import ImmediateHttpResponse
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from django.conf import settings
from django.http import HttpResponseForbidden


def _check_email_domain(email):
    if email.count('@') != 1:
        raise forms.ValidationError('There must be one and only one @s in your email address.')

    if settings.VALID_SIGNUP_DOMAINS == settings.VALID_SIGNUP_DOMAINS_DEFAULT:
        return

    domain = email.split('@')[1]

    if domain not in settings.VALID_SIGNUP_DOMAINS:
        raise forms.ValidationError('Your mail domain not allowed to sign up.')


class DinoSocialAccountAdapter(DefaultSocialAccountAdapter):
    def pre_social_login(self, request, sociallogin):
        u = sociallogin.user
        try:
            _check_email_domain(u.email)
        except forms.ValidationError:
            raise ImmediateHttpResponse(HttpResponseForbidden())

    def is_open_for_signup(self, *args, **kwargs):
        return settings.ENABLE_SOCIAL_SIGNUP


class DinoAccountAdapter(DefaultAccountAdapter):
    def clean_email(self, email):
        _check_email_domain(email)
        return super().clean_email(email)

    def is_open_for_signup(self, *args, **kwargs):
        return settings.ENABLE_EMAIL_SIGNUP
