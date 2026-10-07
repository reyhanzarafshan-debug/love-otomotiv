# Generated manually

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="sitesettings",
            name="phone_secondary",
            field=models.CharField(
                blank=True,
                default="0551 401 40 42",
                max_length=50,
                verbose_name="Telefon 2",
            ),
        ),
        migrations.AlterField(
            model_name="sitesettings",
            name="phone",
            field=models.CharField(
                blank=True,
                default="0551 401 40 41",
                max_length=50,
                verbose_name="Telefon",
            ),
        ),
    ]
