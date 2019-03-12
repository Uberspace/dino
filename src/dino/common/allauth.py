from allauth.account.adapter import DefaultAccountAdapter
from django.conf import settings


class DinoAccountAdapter(DefaultAccountAdapter):
    def is_open_for_signup(self, request):
        return settings.ENABLE_SIGNUP
