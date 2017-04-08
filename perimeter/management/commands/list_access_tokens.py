# -*- coding: utf-8 -*-
"""Management command to list all active tokens."""
from django.core.management.base import BaseCommand

from perimeter.models import AccessToken


class Command(BaseCommand):

    help = "List all active tokens."

    def handle(self, *args, **options):

        self.stdout.write("Listing all tokens:")
        for token in AccessToken.objects.all():
            self.stdout.write(str(token))
