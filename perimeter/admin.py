from django.contrib.admin import site, ModelAdmin

from .models import AccessToken, AccessTokenUse


class AccessTokenAdmin(ModelAdmin):

    raw_id_fields = ('created_by',)
    list_display = ('token', 'expires_on', 'is_active', 'created_at', 'created_by')
    readonly_fields = ('created_at', 'updated_at')

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        """
        Presets the 'created_by' field to the current user.

        Taken from http://stackoverflow.com/a/5633217
        """
        if db_field.name == 'created_by':
            kwargs['initial'] = request.user.id
        return super(AccessTokenAdmin, self).formfield_for_foreignkey(
            db_field, request, **kwargs
        )


site.register(AccessToken, AccessTokenAdmin)


class AccessTokenUseAdmin(ModelAdmin):

    list_display = ('token', 'expires_on', 'timestamp', 'client_ip')
    readonly_fields = ('timestamp', 'client_user_agent', 'client_ip')
    raw_id_fields = ('token',)

    def expires_on(self, obj):
        return obj.token.expires_on
    expires_on.short_description = 'Token Expires'


site.register(AccessTokenUse, AccessTokenUseAdmin)
