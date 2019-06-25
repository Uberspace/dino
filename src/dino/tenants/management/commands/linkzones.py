from django.core.management.base import BaseCommand, CommandError

from dino.synczones.models import Zone
from dino.tenants.models import Tenant
import sys


class Command(BaseCommand):
    help = 'Associate a list of zones with a given tenant'

    def add_arguments(self, parser):
        parser.add_argument('--zone-file', required=True, help='Path of a text file containing a list of fully qualifed zones, separated by newlines.')
        parser.add_argument('--tenant', required=True, help='ID of an existing tenant to add the given zones to.')

    def handle(self, *args, **options):
        with open(options['zone_file']) as f:
            zones = f.read().strip().splitlines()

        tenant = Tenant.objects.get(pk=options['tenant'])

        for zone in zones:
            try:
                zone = Zone.objects.get(name=zone)
            except:
                sys.stderr.write(f"zone {zone} does not exist.\n")
                continue

            tenant.zones.add(zone)
            print(f"{zone} linked")
