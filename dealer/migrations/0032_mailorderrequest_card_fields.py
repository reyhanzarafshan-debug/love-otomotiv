# Mail Order: kart bilgisi alanları

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("dealer", "0031_online_payment_request"),
    ]

    operations = [
        migrations.AddField(
            model_name="mailorderrequest",
            name="card_holder_name",
            field=models.CharField(blank=True, max_length=200, verbose_name="Kart üzerindeki isim"),
        ),
        migrations.AddField(
            model_name="mailorderrequest",
            name="card_number",
            field=models.CharField(blank=True, max_length=50, verbose_name="Kart numarası"),
        ),
        migrations.AddField(
            model_name="mailorderrequest",
            name="expiry_mmyy",
            field=models.CharField(blank=True, max_length=5, verbose_name="Son kullanma (AA/YY)"),
        ),
        migrations.AddField(
            model_name="mailorderrequest",
            name="cvv",
            field=models.CharField(blank=True, max_length=10, verbose_name="CVV"),
        ),
    ]
