# Bayi silinebilsin: siparişlerde dealer SET_NULL

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("dealer", "0004_alter_order_delivery_address_alter_order_order_notes_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="order",
            name="dealer",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="orders",
                to="dealer.dealerprofile",
            ),
        ),
    ]
