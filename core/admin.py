from django.contrib import admin
from django.utils.html import format_html

from .models import SiteSettings


@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    list_display = ("site_name", "phone", "email", "color_preview")
    list_display_links = ("site_name",)

    fieldsets = (
        ("Site / Firma", {"fields": ("site_name", "logo")}),
        ("İletişim", {"fields": ("phone", "phone_secondary", "email", "address")}),
        ("Ödeme (Havale/EFT)", {"fields": ("iban",)}),
        ("Renk teması (hex, örn: #1e3a5f)", {"fields": ("primary_color", "secondary_color", "accent_color")}),
    )

    def color_preview(self, obj):
        if not obj:
            return "—"
        return format_html(
            '<span style="display:inline-block; width:20px; height:20px; background:{}; border:1px solid #ccc; border-radius:4px;"></span> '
            '<span style="display:inline-block; width:20px; height:20px; background:{}; border:1px solid #ccc; border-radius:4px;"></span>',
            obj.primary_color or "#1e3a5f",
            obj.secondary_color or "#0f2942",
        )
    color_preview.short_description = "Tema"

    def has_add_permission(self, request):
        return not SiteSettings.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False
