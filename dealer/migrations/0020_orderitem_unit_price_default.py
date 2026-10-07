# Generated for admin manual order: unit_price can default to 0 for auto-fill on save

from decimal import Decimal

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("dealer", "0019_order_total_amount_and_orderitem_line_total"),
    ]

    operations = [
        migrations.AlterField(
            model_name="orderitem",
            name="unit_price",
            field=models.DecimalField(
                decimal_places=2,
                default=Decimal("0.00"),
                help_text="0 bırakırsanız ürün fiyatı (bayi/misafir) otomatik doldurulur.",
                max_digits=10,
                verbose_name="Birim fiyat (TL)",
            ),
        ),
    ]
