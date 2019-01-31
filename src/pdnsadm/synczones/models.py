from django.db import models


class Zone(models.Model):
    name = models.CharField(primary_key=True, max_length=254)

    def __str__(self):
        return f'Zone {self.name}'

    @staticmethod
    def import_from_powerdns(zones):
        # TODO: remove zones no longer present in powerdns, or maybe present the user with a "this zone has vanished, wanna delete?" view
        Zone.objects.bulk_create(
            (Zone(name=zone.name) for zone in zones),
            ignore_conflicts=True,
        )
