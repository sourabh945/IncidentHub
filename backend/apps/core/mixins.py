from django.apps import apps
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404

from .constants import Role


class OrgRequiredMixin(LoginRequiredMixin):
    """
    Mixin to require the user to be part of an organization.
    And make sure the user have the role to see the page from its role.
    """

    allowed_roles = Role.ALL

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_access(request)

        # checking if the user have the company and membership correct
        Membership = apps.get_model("organization", "Membership")

        membership = get_object_or_404(
            Membership.Objects.select_related("organization"),
            user=request.user,
            organization__slug=kwargs.get("org_slug"),
            organization__is_active=True,
            organization__deleted_at__isnull=True,
        )

        if membership.role not in self.allowed_roles:
            raise PermissionDenied

        request.organization = membership.organization
        request.membership = membership
        return super().dispatch(request, *args, **kwargs)
