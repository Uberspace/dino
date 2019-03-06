import django.forms as forms
from django.core import signing


class SignedHiddenField(forms.CharField):
    widget = forms.HiddenInput

    def to_python(self, value):
        return signing.loads(value)
