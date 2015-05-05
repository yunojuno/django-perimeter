# -*- coding: utf-8 -*-
"""Management command to list all active tokens."""
import logging

from django.core.management.base import BaseCommand
from optparse import make_option

from perimeter.models import AccessToken

logger = logging.getLogger(__name__)


class Command(BaseCommand):

    help = "List all active tokens."

    def handle(self, *args, **options):

        logger.info(u"Listing all tokens:")
        for token in AccessToken.objects.all():
            logger.info(token)
