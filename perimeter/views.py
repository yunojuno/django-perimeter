# -*- coding: utf-8 -*-
# Perimeter app views
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import render

from perimeter.forms import GatewayForm

def gateway(request, template_name='gateway.html'):
    """Display gateway form and process access requests.

    When the PerimeterAccessMiddleware catches an unvalidated
    user request they will redirect to this page.

    """
    if request.method == 'GET':
        form = GatewayForm()

    elif request.method == 'POST':
        form = GatewayForm(request.POST)
        if form.is_valid():
            usage = form.save(request)
            return HttpResponseRedirect(reverse('homepage'))

    return render(request, template_name, {'form': form})
