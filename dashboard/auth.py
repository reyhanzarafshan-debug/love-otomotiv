"""
Role-based access for dashboard panels.
Uses: staff/superuser, auth.Group (Warehouse User, OWNER, PURCHASING, ACCOUNTING, VIEWER), DealerProfile.
"""
from dealer.models import DealerProfile


# Group names that can access management dashboard (in addition to staff/superuser)
MANAGEMENT_GROUPS = {"OWNER", "PURCHASING", "ACCOUNTING", "VIEWER"}
WAREHOUSE_GROUP_NAME = "Warehouse User"


def user_can_management(user):
    if not user or not user.is_authenticated:
        return False
    if user.is_superuser or user.is_staff:
        return True
    return user.groups.filter(name__in=MANAGEMENT_GROUPS).exists()


def user_can_warehouse(user):
    if not user or not user.is_authenticated:
        return False
    return user.groups.filter(name=WAREHOUSE_GROUP_NAME).exists()


def user_can_dealer_panel(user):
    """User has an approved dealer profile (B2B dealer)."""
    if not user or not user.is_authenticated:
        return False
    profile = DealerProfile.objects.filter(user=user).first()
    return profile is not None and profile.is_approved


def get_dealer_profile(user):
    if not user or not user.is_authenticated:
        return None
    return DealerProfile.objects.filter(user=user).first()


def get_panel_redirect_url(user):
    """Return the best dashboard URL for this user (management > warehouse > dealer)."""
    if not user or not user.is_authenticated:
        return None
    if user_can_management(user):
        return "dashboard:management"
    if user_can_warehouse(user):
        return "dashboard:warehouse"
    if user_can_dealer_panel(user):
        return "dashboard:dealer"
    return None
