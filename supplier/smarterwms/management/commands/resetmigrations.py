from django.core.management.base import BaseCommand, CommandError
from django.conf import settings

class Command(BaseCommand):
    help = "Reset migrations for "

    def handle(self, *args, **options):
        baseDir = settings.BASE_DIR
        self.stdout.write(self.style.SUCCESS('Base dir '%baseDir))