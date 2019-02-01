from django.contrib.auth import get_user_model
from django.db import models


class PermissionLevels():
    ADMIN = 'ADMIN'
    USER = 'USER'

    choices = (
        (ADMIN, 'Admin'),
        (USER, 'User'),
    )

    @classmethod
    def max_length(cls):
        return max(c[0] for c in cls.choices)


class Membership(models.Model):
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    tenant = models.ForeignKey('Tenant', on_delete=models.CASCADE)
    level = models.TextField(choices=PermissionLevels.choices, default=PermissionLevels.USER, max_length=PermissionLevels.max_length())

    def __str__(self):
        return f'Membership user {self.user.username} in tenant {self.tenant.name}'


class Tenant(models.Model):
    users = models.ManyToManyField(get_user_model(), through='Membership', related_name='tenants')
    zones = models.ManyToManyField('synczones.Zone', blank=True, related_name='tenants')
    name = models.CharField(max_length=100)

    def __str__(self):
        return f'Tenant {self.name}'
