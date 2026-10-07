# Generated manually for B2B dealer system

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dealer', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('slug', models.SlugField(max_length=100, unique=True)),
            ],
            options={
                'ordering': ['name'],
                'verbose_name_plural': 'Kategoriler',
            },
        ),
        migrations.AddField(
            model_name='product',
            name='category',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='products', to='dealer.category'),
        ),
        migrations.AddField(
            model_name='product',
            name='image',
            field=models.ImageField(blank=True, null=True, upload_to='products/'),
        ),
        migrations.AddField(
            model_name='order',
            name='delivery_address',
            field=models.TextField(blank=True, default='', verbose_name='Teslimat adresi'),
        ),
        migrations.AddField(
            model_name='order',
            name='order_notes',
            field=models.TextField(blank=True, default='', verbose_name='Sipariş notu'),
        ),
        migrations.AlterField(
            model_name='order',
            name='status',
            field=models.CharField(
                choices=[
                    ('pending', 'Beklemede'),
                    ('approved', 'Onaylandı'),
                    ('preparing', 'Hazırlanıyor'),
                    ('shipped', 'Kargoda'),
                    ('delivered', 'Teslim'),
                    ('cancelled', 'İptal'),
                ],
                default='pending',
                max_length=20,
            ),
        ),
        migrations.RemoveField(
            model_name='order',
            name='payment_method',
        ),
    ]
