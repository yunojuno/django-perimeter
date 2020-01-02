from __future__ import annotations

from typing import TYPE_CHECKING

from django import forms
from django.core.exceptions import ValidationError
from django.http import HttpRequest

from .models import AccessToken
from .settings import PERIMETER_SESSION_KEY

if TYPE_CHECKING:
    from .models import AccessTokenUse


class TokenGatewayForm(forms.Form):
    """Form used to process a perimeter request."""

    token = forms.CharField(required=True, max_length=100)

    def clean_token(self) -> AccessToken:
        """Validate the token against existing tokens."""
        try:
            _token = AccessToken.objects.get(token=self.cleaned_data.get("token"))
            if _token.has_expired:
                raise ValidationError("Token has expired", code="expired")
            if not _token.is_active:
                raise ValidationError("Token is inactive", code="invalid")
        except AccessToken.DoesNotExist:
            raise ValidationError("Token not found", code="invalid")
        else:
            self._token = _token
            return _token

    def save_token(self, request: HttpRequest) -> AccessTokenUse:
        """Record use of the token."""
        request.session[PERIMETER_SESSION_KEY] = self._token.token
        return self._token.record(
            user_email=self.cleaned_data.get("email"),
            user_name=self.cleaned_data.get("name"),
            client_ip=request.META.get("REMOTE_ADDR", "unknown"),
            client_user_agent=request.META.get("HTTP_USER_AGENT", "unknown"),
        )

    def save(self, request: HttpRequest) -> AccessTokenUse:
        """Create a new AccessTokenUse object from the form."""
        if getattr(self, "_token", None) is None:
            raise ValueError("Form token attr is not set")
        return self.save_token(request)


class UserGatewayForm(TokenGatewayForm):
    """Form used to process a perimeter request with user info."""

    email = forms.EmailField(required=True)
    name = forms.CharField(required=True, max_length=100)
