import django.forms as forms
from django.core import signing


class SignedHiddenField(forms.CharField):
    widget = forms.HiddenInput

    def to_python(self, value):
        if not value:
            return None
        return signing.loads(value)
