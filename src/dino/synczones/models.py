from django.db import models


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
