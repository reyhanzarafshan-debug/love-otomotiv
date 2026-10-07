# Generated manually for order pricing professionalization

from decimal import Decimal

from django.db import migrations, models


def backfill_line_total_and_order_total(apps, schema_editor):
    Order = apps.get_model("dealer", "Order")
    OrderItem = apps.get_model("dealer", "OrderItem")
    for item in OrderItem.objects.all():
        item.line_total = (item.unit_price or Decimal("0")) * (item.quantity or 1)
        item.save(update_fields=["line_total"])
    for order in Order.objects.all():
        total = sum(
            (item.line_total or Decimal("0"))
            for item in order.items.all()
        )
        order.total_amount = total
        order.save(update_fields=["total_amount"])


def noop_reverse(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ("dealer", "0018_add_order_source"),
    ]

    operations = [
        migrations.AddField(
            model_name="order",
            name="total_amount",
            field=models.DecimalField(
                decimal_places=2,
                default=Decimal("0.00"),
                help_text="Sipariş kalemlerinin toplamı; OrderItem kaydedilince otomatik güncellenir.",
                max_digits=12,
                verbose_name="Toplam tutar (TL)",
            ),
        ),
        migrations.AddField(
            model_name="orderitem",
            name="line_total",
            field=models.DecimalField(
                decimal_places=2,
                default=Decimal("0.00"),
                help_text="quantity × unit_price; kayıt sırasında otomatik hesaplanır.",
                max_digits=12,
                verbose_name="Satır toplamı (TL)",
            ),
        ),
        migrations.RunPython(backfill_line_total_and_order_total, noop_reverse),
    ]
