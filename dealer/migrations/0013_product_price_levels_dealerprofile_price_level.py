# B2B price levels: Product price, price_a, price_b, price_c; DealerProfile price_level

from decimal import Decimal
from django.db import migrations, models


def set_product_price_from_dealer(apps, schema_editor):
    """Set Product.price from dealer_price for existing rows."""
    Product = apps.get_model("dealer", "Product")
    for p in Product.objects.all():
        if hasattr(p, "dealer_price") and p.dealer_price is not None:
            p.price = p.dealer_price
        else:
            p.price = Decimal("0")
        p.save(update_fields=["price"])


class Migration(migrations.Migration):

    dependencies = [
        ("dealer", "0012_alter_dealerprofile_address_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="product",
            name="price",
            field=models.DecimalField(
                decimal_places=2,
                default=Decimal("0"),
                help_text="Varsayılan / liste fiyatı; A/B/C boşsa buna düşer.",
                max_digits=10,
                verbose_name="Liste fiyatı",
            ),
        ),
        migrations.AddField(
            model_name="product",
            name="price_a",
            field=models.DecimalField(
                blank=True,
                decimal_places=2,
                help_text="B2B fiyat seviyesi A.",
                max_digits=10,
                null=True,
                verbose_name="Fiyat A",
            ),
        ),
        migrations.AddField(
            model_name="product",
            name="price_b",
            field=models.DecimalField(
                blank=True,
                decimal_places=2,
                help_text="B2B fiyat seviyesi B.",
                max_digits=10,
                null=True,
                verbose_name="Fiyat B",
            ),
        ),
        migrations.AddField(
            model_name="product",
            name="price_c",
            field=models.DecimalField(
                blank=True,
                decimal_places=2,
                help_text="B2B fiyat seviyesi C.",
                max_digits=10,
                null=True,
                verbose_name="Fiyat C",
            ),
        ),
        migrations.AddField(
            model_name="dealerprofile",
            name="price_level",
            field=models.CharField(
                choices=[("a", "A"), ("b", "B"), ("c", "C")],
                default="b",
                max_length=1,
                verbose_name="Fiyat seviyesi",
            ),
        ),
        migrations.RunPython(set_product_price_from_dealer, migrations.RunPython.noop),
    ]
