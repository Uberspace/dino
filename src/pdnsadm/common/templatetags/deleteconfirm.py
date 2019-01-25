import django.core.signing as signing
from django import template

register = template.Library()

@register.filter(name='sign')
def sign(value):
    return signing.dumps(value)
