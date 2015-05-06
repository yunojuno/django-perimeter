# -*- coding: utf-8 -*-
"""Management command to list all active tokens."""
from django.core.management.base import BaseCommand
from optparse import make_option

from perimeter.models import AccessToken


class Command(BaseCommand):

    help = "List all active tokens."

    def handle(self, *args, **options):

        print (u"Listing all tokens:")
        for token in AccessToken.objects.all():
            print (token)
