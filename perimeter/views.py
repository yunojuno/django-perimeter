from urllib.parse import unquote

from django.http import HttpResponseRedirect
from django.http.request import HttpRequest
from django.http.response import HttpResponse, HttpResponseNotAllowed
from django.shortcuts import render
from django.urls import Resolver404, resolve, reverse

from .forms import TokenGatewayForm, UserGatewayForm
from .settings import PERIMETER_REQUIRE_USER_DETAILS


def resolve_return_url(return_url: str) -> str:
    """
    Resolve a URL to confirm that it's valid.

    Before redirecting to a return_url, use the resolve function
    to confirm that it matches a valid view function.

    If the resolver can't find the function, return the only url we
    know exists - perimeter:gateway

    """
    path = None
    if return_url:
        return_url = unquote(return_url)
        # Path with a query string will not resolve, so we strip it for the check.
        path = return_url.split("?")[0]

    try:
        resolve(path)
        return return_url
    except Resolver404:
        return reverse("perimeter:gateway")


def gateway(
    request: HttpRequest, template_name: str = "perimeter/gateway.html"
) -> HttpResponse:
    """
    Display gateway form and process access requests.

    When the PerimeterAccessMiddleware catches an unvalidated
    user request they will redirect to this page.

    """
    # the form to use is based on whether we want user details or not.
    klass = UserGatewayForm if PERIMETER_REQUIRE_USER_DETAILS else TokenGatewayForm

    if request.method == "GET":
        form = klass()

    elif request.method == "POST":
        form = klass(request.POST)
        if form.is_valid():
            form.save(request)
            return HttpResponseRedirect(resolve_return_url(request.GET.get("next")))

    else:
        return HttpResponseNotAllowed(["GET", "POST"])

    return render(request, template_name, {"form": form})
