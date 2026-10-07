# Generated for admin: manual price override checkbox

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("dealer", "0020_orderitem_unit_price_default"),
    ]

    operations = [
        migrations.AddField(
            model_name="orderitem",
            name="manual_price_override",
            field=models.BooleanField(
                default=False,
                help_text="İşaretlenirse birim fiyat düzenlenebilir; işaretli değilse ürün fiyatı otomatik kullanılır.",
                verbose_name="Fiyatı elle gir",
            ),
        ),
    ]
