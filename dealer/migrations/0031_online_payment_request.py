# Generated for OnlinePaymentRequest (PayTR online payment)

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("dealer", "0030_bank_transfer_notice"),
    ]

    operations = [
        migrations.CreateModel(
            name="OnlinePaymentRequest",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("provider", models.CharField(default="paytr", max_length=20, verbose_name="Sağlayıcı")),
                ("amount", models.DecimalField(decimal_places=2, max_digits=12, verbose_name="Tutar (₺)")),
                ("merchant_oid", models.CharField(db_index=True, max_length=64, unique=True, verbose_name="Mağaza sipariş no")),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("pending", "Beklemede"),
                            ("success", "Başarılı"),
                            ("failed", "Başarısız"),
                            ("cancelled", "İptal"),
                        ],
                        default="pending",
                        max_length=20,
                        verbose_name="Durum",
                    ),
                ),
                ("payment_date", models.DateTimeField(blank=True, null=True, verbose_name="Ödeme tarihi")),
                ("external_reference", models.CharField(blank=True, max_length=255, null=True, verbose_name="Dış referans")),
                ("failed_reason_code", models.CharField(blank=True, max_length=50, null=True, verbose_name="Hata kodu")),
                ("failed_reason_message", models.TextField(blank=True, null=True, verbose_name="Hata mesajı")),
                ("callback_payload", models.TextField(blank=True, null=True, verbose_name="Callback ham veri")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "dealer",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="online_payment_requests",
                        to="dealer.dealerprofile",
                    ),
                ),
                (
                    "related_payment",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="online_payment_requests",
                        to="dealer.dealerpayment",
                        verbose_name="Oluşan ödeme kaydı",
                    ),
                ),
            ],
            options={
                "verbose_name": "Online ödeme talebi",
                "verbose_name_plural": "Online ödeme talepleri",
                "ordering": ["-created_at"],
            },
        ),
    ]
