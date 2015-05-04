# -*- coding: utf-8 -*-
# perimeter forms
from django import forms
from django.core.exceptions import ValidationError

from perimeter.middleware import set_request_token
from perimeter.models import AccessToken, AccessTokenUse

class GatewayForm(forms.Form):
    """Form used to process a perimeter request.

    This form does **not** validate the token, it only
    confirms that the user has put in a valid token format.

    if form.is_valid():
        if form.token.is_valid():
            form.save()
        else:

    """
    token = forms.CharField(required=True, max_length=100)
    email = forms.EmailField(required=True)
    name = forms.CharField(required=True, max_length=100)

    def clean_token(self):
        """Validate the token against existing tokens."""
        try:
            _token = self.cleaned_data.get('token')
            self.token = AccessToken.objects.get(token=_token)
            if self.token.is_valid:
                return _token
            if self.token.has_expired:
                raise ValidationError(u"Token has expired", code="expired")
            if not self.token.is_active:
                raise ValidationError(u"Token is inactive", code="invalid")
        except AccessToken.DoesNotExist:
            raise ValidationError(u"Token not found", code="invalid")
        # # token is marked as unique, so in theory this will never happen
        # # and is impossible to test without mocking
        # except AccessToken.MultipleObjectsReturned:
        #     raise ValidationError(u"Ambiguous token value", code="invalid")

    def save(self, request):
        """Create a new AccessTokenUse object from the form."""
        assert getattr(self, 'token', None) is not None, "Form token attr is not set"
        set_request_token(request, self.token.token)
        return self.token.record(
            user_email=self.cleaned_data.get('email'),
            user_name=self.cleaned_data.get('name'),
            client_ip=request.META.get('REMOTE_ADDR','unknown'),
            client_user_agent=request.META.get('HTTP_USER_AGENT', 'unknown'),
        )
