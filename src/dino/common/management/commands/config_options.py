from django.core.management.base import BaseCommand

from dino.settings import cfg


class Command(BaseCommand):
    help = 'Show all available configuration options.'

    def handle(self, *args, **options):
        print(cfg.settings_plaintext())
