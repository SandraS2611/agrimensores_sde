# en admin.py
from django.contrib import admin
from django.core.exceptions import PermissionDenied

class SuperuserOnlyAdminSite(admin.AdminSite):
    def has_permission(self, request):
        if not request.user.is_active or not request.user.is_superuser:
            raise PermissionDenied
        return True

admin_site = SuperuserOnlyAdminSite(name="superuser_admin")
