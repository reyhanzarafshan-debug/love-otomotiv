from .models import SiteSettings


def site_settings(request):
    """Tüm şablonlarda site_settings kullanılabilir."""
    return {"site_settings": SiteSettings.get()}
