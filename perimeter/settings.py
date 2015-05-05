# -*- coding: utf-8 -*-
# perimeter settings file
from django.conf import settings
# if False, the middleware will be disabled
PERIMETER_ENABLED = getattr(settings, 'PERIMETER_ENABLED', True)
# request.session key used to store user's token
PERIMETER_SESSION_KEY = getattr(settings, 'PERIMETER_SESSION_KEY', "perimeter")
# default expiry, in days, of a token
PERIMETER_DEFAULT_EXPIRY = getattr(settings, 'PERIMETER_DEFAULT_EXPIRY', 7)
