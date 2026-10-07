# B model: stock_on_hand, stock_reserved; mevcut stock_quantity -> stock_on_hand taşınır

from django.db import migrations, models


def copy_stock_quantity_to_on_hand(apps, schema_editor):
    Product = apps.get_model("dealer", "Product")
    for p in Product.objects.all():
        p.stock_on_hand = getattr(p, "stock_quantity", 0) or 0
        p.stock_reserved = 0
        p.save(update_fields=["stock_on_hand", "stock_reserved"])


def noop(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ("dealer", "0008_dealerprofile_total_debt_last_due_date"),
    ]

    operations = [
        migrations.AddField(
            model_name="product",
            name="stock_on_hand",
            field=models.PositiveIntegerField(default=0, verbose_name="Eldeki stok"),
        ),
        migrations.AddField(
            model_name="product",
            name="stock_reserved",
            field=models.PositiveIntegerField(default=0, verbose_name="Rezerve stok"),
        ),
        migrations.RunPython(copy_stock_quantity_to_on_hand, noop),
        migrations.RemoveField(
            model_name="product",
            name="stock_quantity",
        ),
    ]
