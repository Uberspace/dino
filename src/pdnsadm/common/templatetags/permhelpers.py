from django import template
from django.utils.safestring import SafeString

register = template.Library()

@register.simple_tag()
def btn_perm(perm, user, *args):
    if user.has_perm(perm, *args):
        return ""
    else:
        return SafeString(" disabled title='permission denied' ")
