# -*- coding: utf-8 -*-
# Perimeter app views
import urllib

from django.core.urlresolvers import reverse, resolve, Resolver404
from django.http import HttpResponseRedirect
from django.shortcuts import render

from perimeter.forms import GatewayForm


def resolve_return_url(return_url):
    """Resolve a URL to confirm that it's valid.

    Before redirecting to a return_url, use the resolve function
    to confirm that it matches a valid view function.

    If the resolver can't find the function, return the only url we
    know exists - perimeter:gateway

    """
    path = None
    if return_url:
        return_url = urllib.unquote(return_url)
        # Path with a query string will not resolve, so we strip it for the check.
        path = return_url.split("?")[0]

    try:
        resolve(path)
        return return_url
    except Resolver404:
        return reverse('perimeter:gateway')


def gateway(request, template_name='perimeter/gateway.html'):
    """Display gateway form and process access requests.

    When the PerimeterAccessMiddleware catches an unvalidated
    user request they will redirect to this page.

    """
    if request.method == 'GET':
        form = GatewayForm()

    elif request.method == 'POST':
        form = GatewayForm(request.POST)
        if form.is_valid():
            form.save(request)
            return HttpResponseRedirect(
                resolve_return_url(
                    request.GET.get('next'))
            )

    return render(request, template_name, {'form': form})
