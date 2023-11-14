# -*- coding: utf-8 -*-
"""Management command to list all active tokens."""
from typing import Any

from django.core.management.base import BaseCommand

from perimeter.models import AccessToken


class Command(BaseCommand):
    help = "List all active tokens."  # noqa: A003

    def handle(self, *args: Any, **options: Any) -> None:
        self.stdout.write("Listing all tokens:")
        for token in AccessToken.objects.all():
            prefix = "- " if token.is_valid else "x "
            suffix = " expired " if token.has_expired else " expires "
            self.stdout.write(f"{prefix} {token} {suffix} {token.expires_on}")
