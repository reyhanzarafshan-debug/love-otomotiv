from .auth import get_panel_redirect_url, user_can_dealer_panel, user_can_management, user_can_warehouse


def dashboard_nav(request):
    if not request.user.is_authenticated:
        return {
            "dashboard_can_management": False,
            "dashboard_can_warehouse": False,
            "dashboard_can_dealer": False,
            "dashboard_panel_url": None,
        }
    return {
        "dashboard_can_management": user_can_management(request.user),
        "dashboard_can_warehouse": user_can_warehouse(request.user),
        "dashboard_can_dealer": user_can_dealer_panel(request.user),
        "dashboard_panel_url": get_panel_redirect_url(request.user),
    }
