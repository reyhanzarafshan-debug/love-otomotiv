# Generated manually - stok ve bayi finans

from decimal import Decimal
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("dealer", "0005_alter_order_dealer_on_delete"),
    ]

    operations = [
        migrations.AddField(
            model_name="dealerprofile",
            name="credit_limit",
            field=models.DecimalField(
                decimal_places=2,
                default=Decimal("50000.00"),
                help_text="Toplam borç bu limiti aşamaz.",
                max_digits=12,
                verbose_name="Kredi limiti (TL)",
            ),
        ),
        migrations.AddField(
            model_name="dealerprofile",
            name="is_locked",
            field=models.BooleanField(
                default=False,
                help_text="Vade geçtiği ve ödeme yapılmadığında kilitlenir; sipariş veremez.",
                verbose_name="Hesap kilitli",
            ),
        ),
        migrations.AddField(
            model_name="order",
            name="due_date",
            field=models.DateField(
                blank=True,
                help_text="Sadece bayi siparişlerinde; sipariş tarihinden 30 iş günü sonrası.",
                null=True,
                verbose_name="Vade tarihi (30 iş günü)",
            ),
        ),
        migrations.CreateModel(
            name="DealerPayment",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("amount", models.DecimalField(decimal_places=2, max_digits=12, verbose_name="Tutar (TL)")),
                ("payment_date", models.DateTimeField(auto_now_add=True, verbose_name="Ödeme tarihi")),
                ("note", models.CharField(blank=True, max_length=255, verbose_name="Açıklama")),
                (
                    "dealer",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="payments",
                        to="dealer.dealerprofile",
                    ),
                ),
            ],
            options={
                "verbose_name": "Bayi ödemesi",
                "verbose_name_plural": "Bayi ödemeleri",
                "ordering": ["-payment_date"],
            },
        ),
    ]
