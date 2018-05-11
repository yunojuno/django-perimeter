from django import forms
from django.core.exceptions import ValidationError

from .middleware import set_request_token
from .models import AccessToken


class TokenGatewayForm(forms.Form):

    """Form used to process a perimeter request."""

    token = forms.CharField(required=True, max_length=100)

    def clean_token(self):
        """Validate the token against existing tokens."""
        try:
            _token = self.cleaned_data.get('token')
            self.token = AccessToken.objects.get(token=_token)
            if self.token.is_valid:
                return _token
            if self.token.has_expired:
                raise ValidationError("Token has expired", code="expired")
            if not self.token.is_active:
                raise ValidationError("Token is inactive", code="invalid")
        except AccessToken.DoesNotExist:
            raise ValidationError("Token not found", code="invalid")

    def save(self, request):
        """Create a new AccessTokenUse object from the form."""
        assert getattr(self, 'token', None) is not None, "Form token attr is not set"
        set_request_token(request, self.token.token)
        return self.token.record(
            user_email=self.cleaned_data.get('email'),
            user_name=self.cleaned_data.get('name'),
            client_ip=request.META.get('REMOTE_ADDR', 'unknown'),
            client_user_agent=request.META.get('HTTP_USER_AGENT', 'unknown'),
        )


class UserGatewayForm(TokenGatewayForm):

    """Form used to process a perimeter request with user info."""

    email = forms.EmailField(required=True)
    name = forms.CharField(required=True, max_length=100)
