from django.contrib import admin
from django.contrib.auth.models import User, Group
from django.contrib.auth.admin import UserAdmin, GroupAdmin

from rest_framework_simplejwt.token_blacklist.models import BlacklistedToken, OutstandingToken
from rest_framework_simplejwt.token_blacklist.admin import BlacklistedTokenAdmin, OutstandingTokenAdmin


# Unregister the default User and Group admin
admin.site.unregister(User)
# Remove django user group functionality    
admin.site.unregister(Group)

admin.site.unregister(OutstandingToken)
admin.site.unregister(BlacklistedToken)

class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'is_staff', 'is_active', 'date_joined', 'last_login')
    list_filter = ['is_staff', 'is_active']
    search_fields = ['username']

class CustomTokenAdmin(OutstandingTokenAdmin):
    list_display = ('jti', 'user', 'created_at', 'expires_at')
    search_fields = ('user__username',)
    list_filter = ('user', 'created_at', 'expires_at')
    ordering = ('-created_at',)

    def has_delete_permission(self, *args, **kwargs):
        return True  # Allows deletion of tokens
    
class CustomBlackListedTokenAdmin(BlacklistedTokenAdmin):
    pass;  # Use the default admin settings

# Register with custom names
User._meta.verbose_name = 'User Account'
User._meta.verbose_name_plural = 'User Accounts'

OutstandingToken._meta.verbose_name = 'Access Token'
OutstandingToken._meta.verbose_name_plural = 'Access Tokens'
BlacklistedToken._meta.verbose_name = 'Revoked Token'
BlacklistedToken._meta.verbose_name_plural = 'Revoked Tokens'

# Register the models with custom admin classes
admin.site.register(User, CustomUserAdmin)
admin.site.register(OutstandingToken, CustomTokenAdmin)
admin.site.register(BlacklistedToken, BlacklistedTokenAdmin)
