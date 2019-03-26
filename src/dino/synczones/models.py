from django.contrib.auth import get_user_model
from django.db import models
from django.utils.translation import gettext_lazy as _


class Zone(models.Model):
    name = models.CharField(primary_key=True, max_length=254)

    def __str__(self):
        return f'Zone {self.name}'

    @staticmethod
    def import_from_powerdns(zones):
        Zone.objects.bulk_create(
            (Zone(name=zone) for zone in zones),
            ignore_conflicts=True,
        )

    def log_action(self, user, action, record=None):
        ZoneLogEntry.objects.create(
            user=user,
            user_username=user.username,
            action=action,
            zone=self,
            record=' '.join(record),
        )


class LogAction():
    CREATED = 'CREATED'
    UPDATED = 'UPDATED'
    DELETED = 'DELETED'

    choices = (
        (CREATED, _('created')),
        (UPDATED, _('updated')),
        (DELETED, _('deleted')),
    )

    @classmethod
    def max_length(cls):
        return max(len(c[0]) for c in cls.choices)


class ZoneLogEntry(models.Model):
    date = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(get_user_model(), null=True, on_delete=models.SET_NULL)
    user_username = models.CharField(max_length=150)
    action = models.CharField(max_length=LogAction.max_length(), choices=LogAction.choices)
    zone = models.ForeignKey(Zone, on_delete=models.CASCADE)
    record = models.CharField(max_length=300, blank=True, null=True)
