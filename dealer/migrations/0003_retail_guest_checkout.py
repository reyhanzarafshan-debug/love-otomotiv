# Guest checkout + retail_price / dealer_price

from django.db import migrations, models
import django.db.models.deletion


def copy_price_to_retail_dealer(apps, schema_editor):
    Product = apps.get_model("dealer", "Product")
    for p in Product.objects.all():
        if hasattr(p, "price"):
            p.retail_price = p.price
            p.dealer_price = p.price
            p.save(update_fields=["retail_price", "dealer_price"])


def noop(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ("dealer", "0002_b2b_cart_and_categories"),
    ]

    operations = [
        migrations.AddField(
            model_name="product",
            name="retail_price",
            field=models.DecimalField(
                decimal_places=2, default=0, max_digits=10, verbose_name="Perakende fiyat"
            ),
        ),
        migrations.AddField(
            model_name="product",
            name="dealer_price",
            field=models.DecimalField(
                decimal_places=2, default=0, max_digits=10, verbose_name="Bayi fiyat"
            ),
        ),
        migrations.RunPython(copy_price_to_retail_dealer, noop),
        migrations.RemoveField(model_name="product", name="price"),
        migrations.AddField(
            model_name="order",
            name="customer_name",
            field=models.CharField(blank=True, max_length=200, verbose_name="Müşteri adı"),
        ),
        migrations.AddField(
            model_name="order",
            name="customer_phone",
            field=models.CharField(blank=True, max_length=50, verbose_name="Telefon"),
        ),
        migrations.AddField(
            model_name="order",
            name="customer_email",
            field=models.EmailField(blank=True, max_length=254, verbose_name="E-posta"),
        ),
        migrations.AlterField(
            model_name="order",
            name="dealer",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="orders",
                to="dealer.dealerprofile",
            ),
        ),
        migrations.AlterField(
            model_name="order",
            name="status",
            field=models.CharField(
                choices=[
                    ("pending", "Beklemede"),
                    ("approved", "Onaylandı"),
                    ("shipped", "Kargoda"),
                    ("delivered", "Teslim Edildi"),
                ],
                default="pending",
                max_length=20,
            ),
        ),
    ]
