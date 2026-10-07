from django.db import models


class SiteSettings(models.Model):
    """
    Tek satırlık site ayarları (singleton).
    Admin panelinden firma adı, logo, iletişim, IBAN ve renk teması değiştirilebilir.
    """
    site_name = models.CharField("Site / Firma adı", max_length=200, default="LOVE Otomotive")
    logo = models.ImageField("Logo", upload_to="settings/", blank=True, null=True)
    phone = models.CharField("Telefon", max_length=50, blank=True, default="0551 401 40 41")
    phone_secondary = models.CharField("Telefon 2", max_length=50, blank=True, default="0551 401 40 42")
    email = models.EmailField("E-posta", blank=True, default="info@example.com")
    address = models.TextField("Adres", blank=True, default="")
    iban = models.CharField("Havale/EFT IBAN", max_length=100, blank=True, default="TR00 0000 0000 0000 0000 0000 00")
    # Renk teması (hex)
    primary_color = models.CharField("Ana renk (hex)", max_length=7, default="#1e3a5f")
    secondary_color = models.CharField("İkincil renk (hex)", max_length=7, default="#0f2942")
    accent_color = models.CharField("Vurgu rengi (hex)", max_length=7, default="#2563eb")

    class Meta:
        verbose_name = "Site ayarları"
        verbose_name_plural = "Site ayarları"

    def __str__(self):
        return self.site_name or "Site ayarları"

    @classmethod
    def get(cls):
        """Tek kayıt döndürür; yoksa varsayılanla oluşturur."""
        obj, _ = cls.objects.get_or_create(
            pk=1,
            defaults={
                "site_name": "LOVE Otomotive",
                "phone": "0551 401 40 41",
                "phone_secondary": "0551 401 40 42",
                "email": "info@example.com",
                "iban": "TR00 0000 0000 0000 0000 0000 00",
                "primary_color": "#1e3a5f",
                "secondary_color": "#0f2942",
                "accent_color": "#2563eb",
            },
        )
        return obj
