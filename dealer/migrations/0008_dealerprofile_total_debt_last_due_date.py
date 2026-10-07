# Generated manually - DealerProfile total_debt, last_due_date

from decimal import Decimal
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("dealer", "0007_alter_order_status"),
    ]

    operations = [
        migrations.AddField(
            model_name="dealerprofile",
            name="total_debt",
            field=models.DecimalField(
                decimal_places=2,
                default=Decimal("0.00"),
                max_digits=12,
                verbose_name="Toplam borç (TL)",
            ),
        ),
        migrations.AddField(
            model_name="dealerprofile",
            name="last_due_date",
            field=models.DateField(
                blank=True,
                null=True,
                verbose_name="Son vade tarihi",
            ),
        ),
    ]
