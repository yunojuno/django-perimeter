# -*- coding: utf-8 -*-
"""Management command to create a new AccessToken."""
import datetime
from optparse import make_option

from django.core.management.base import BaseCommand
from django.utils.timezone import now
from django.db.utils import IntegrityError

from perimeter.models import AccessToken
from perimeter.settings import PERIMETER_DEFAULT_EXPIRY


class Command(BaseCommand):

    help = "Create a perimeter access token."

    option_list = BaseCommand.option_list + (
        make_option(
            '-t', '--token',
            action='store',
            dest='token',
            help='User supplied token (max 10 chars)'
        ),
        make_option(
            '-e', '--expires',
            type='int',
            action='store',
            dest='expires',
            help='Expires value (in days)'
        ),
    )

    def handle(self, *args, **options):

        has_expires = options.get('expires') is not None
        days = options.get('expires') or PERIMETER_DEFAULT_EXPIRY
        token = options.get('token') or AccessToken.random_token_value()
        expires_on = (now() + datetime.timedelta(days=days)).date()
        try:
            access_token = AccessToken.objects.create_access_token(
                token=token,
                expires_on=expires_on
            )
            print (
                'Created new access token: "%s" (expires %s)'
                % (access_token.token, access_token.expires_on)
            )
        except IntegrityError:
            access_token = AccessToken.objects.get(token=token)
            if has_expires:
                print("Extending existing token")
                access_token.expires_on = expires_on
                access_token.save()
                print("Token extended: %s" % access_token)
            else:
                print("Token exists already - please use --expires option to extend.")
