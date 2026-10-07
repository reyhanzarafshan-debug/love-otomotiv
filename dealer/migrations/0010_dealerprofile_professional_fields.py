# Professional Dealer (B2B) fields

from decimal import Decimal
from django.conf import settings
from django.db import migrations, models
from django.utils import timezone
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("dealer", "0009_product_stock_on_hand_reserved"),
    ]

    operations = [
        migrations.AddField(
            model_name="dealerprofile",
            name="contact_person",
            field=models.CharField(blank=True, max_length=200, verbose_name="Yetkili kişi"),
        ),
        migrations.AddField(
            model_name="dealerprofile",
            name="email",
            field=models.EmailField(blank=True, max_length=254, verbose_name="E-posta"),
        ),
        migrations.AddField(
            model_name="dealerprofile",
            name="tax_number",
            field=models.CharField(blank=True, max_length=20, verbose_name="Vergi numarası"),
        ),
        migrations.AddField(
            model_name="dealerprofile",
            name="current_debt",
            field=models.DecimalField(
                decimal_places=2,
                default=Decimal("0.00"),
                max_digits=12,
                verbose_name="Cari borç (TL)",
            ),
        ),
        migrations.AddField(
            model_name="dealerprofile",
            name="payment_term_days",
            field=models.PositiveIntegerField(
                default=30,
                help_text="Ödeme vadesi, gün cinsinden.",
                verbose_name="Vade (gün)",
            ),
        ),
        migrations.AddField(
            model_name="dealerprofile",
            name="is_active",
            field=models.BooleanField(default=True, verbose_name="Aktif"),
        ),
        migrations.AddField(
            model_name="dealerprofile",
            name="risk_warning",
            field=models.BooleanField(
                default=False,
                help_text="Riskli bayi işaretlendi.",
                verbose_name="Risk uyarısı",
            ),
        ),
        migrations.AddField(
            model_name="dealerprofile",
            name="created_at",
            field=models.DateTimeField(
                auto_now_add=True,
                default=timezone.now,
                verbose_name="Oluşturulma",
            ),
        ),
        migrations.AlterModelOptions(
            name="dealerprofile",
            options={
                "ordering": ["-created_at"],
                "verbose_name": "Bayi (Dealer)",
                "verbose_name_plural": "Bayiler (Dealers)",
            },
        ),
        migrations.AlterField(
            model_name="dealerprofile",
            name="user",
            field=models.OneToOneField(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="dealer_profile",
                to=settings.AUTH_USER_MODEL,
                verbose_name="Kullanıcı hesabı",
            ),
        ),
    ]
