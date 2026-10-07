# Hard order block: order_block_override

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("dealer", "0014_create_test_product_abc"),
    ]

    operations = [
        migrations.AddField(
            model_name="dealerprofile",
            name="order_block_override",
            field=models.BooleanField(
                default=False,
                help_text="Açıksa riskli olsa bile sipariş verebilir (özel izin).",
                verbose_name="Sipariş engeli muafiyeti",
            ),
        ),
    ]
