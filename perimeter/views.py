# -*- coding: utf-8 -*-
# Perimeter app views
from django.shortcuts import render

from perimeter.forms import GatewayForm

def gateway(request, template_name='gateway.html'):
    """Display gateway form and process access requests.

    When the PerimeterAccessMiddleware catches an unvalidated
    user request they will redirect to this page.
    """

    if request.method == 'GET':
        form = GatewayForm()
        return render(
            request,
            template_name,
            {
                'form': form,
            }
        )

    elif request.method == 'POST':
        return post(request)

    def post(request):
        pass
