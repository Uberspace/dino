from django.contrib.auth import get_user_model
from django.db import models


class Membership(models.Model):
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    tenant = models.ForeignKey('Tenant', on_delete=models.CASCADE)

    def __str__(self):
        return f'Membership user {self.user.username} in tenant {self.tenant.name}'


class Tenant(models.Model):
    users = models.ManyToManyField(get_user_model(), through='Membership')
    zones = models.ManyToManyField('synczones.Zone', blank=True)
    name = models.CharField(max_length=100)

    def __str__(self):
        return f'Tenant {self.name}'
