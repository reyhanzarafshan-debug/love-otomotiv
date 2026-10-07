# Test product with A/B/C prices for verification

from decimal import Decimal
from django.db import migrations


def create_test_product(apps, schema_editor):
    Product = apps.get_model("dealer", "Product")
    if Product.objects.filter(sku="TEST-ABC").exists():
        return
    Product.objects.create(
        name="Test Ürün (A/B/C Fiyat)",
        sku="TEST-ABC",
        description="B2B fiyat seviyesi testi için. A=100, B=120, C=150, liste=99.",
        price=Decimal("99.00"),
        price_a=Decimal("100.00"),
        price_b=Decimal("120.00"),
        price_c=Decimal("150.00"),
        retail_price=Decimal("199.00"),
        dealer_price=Decimal("120.00"),
        is_active=True,
    )


def noop(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ("dealer", "0013_product_price_levels_dealerprofile_price_level"),
    ]

    operations = [
        migrations.RunPython(create_test_product, noop),
    ]
