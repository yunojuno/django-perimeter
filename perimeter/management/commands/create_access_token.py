# -*- coding: utf-8 -*-
"""Management command to create a new AccessToken."""
from django.core.management.base import BaseCommand
from optparse import make_option

from perimeter.models import AccessToken


class Command(BaseCommand):

    help = "Create a perimeter access token."

    option_list = BaseCommand.option_list + (
        make_option(
            '-t', '--token',
            action='store',
            dest='token',
            help='User supplied token (max 10 chars)'
        ),
    )

    def handle(self, *args, **options):

        if options.get('token'):
            token = AccessToken.objects.create_access_token(
                token=options.get('token')
            )
        else:
            token = AccessToken.objects.create_access_token()

        print ('Created new access token: "%s"' % token.token)