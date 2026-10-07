# DealerPayment: description, created_by, created_at; payment_date DateTime -> Date

from django.conf import settings
from django.db import migrations, models
from django.utils import timezone


def payment_date_to_date(apps, schema_editor):
    DealerPayment = apps.get_model("dealer", "DealerPayment")
    today = timezone.now().date()
    for p in DealerPayment.objects.all():
        old = getattr(p, "payment_date", None)
        if old is not None and hasattr(old, "date"):
            p.payment_date_new = old.date()
        else:
            p.payment_date_new = today
        p.save(update_fields=["payment_date_new"])


def noop(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ("dealer", "0015_dealerprofile_order_block_override"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name="dealerpayment",
            name="description",
            field=models.TextField(blank=True, verbose_name="Açıklama"),
        ),
        migrations.AddField(
            model_name="dealerpayment",
            name="created_by",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=models.SET_NULL,
                related_name="dealer_payments_created",
                to=settings.AUTH_USER_MODEL,
                verbose_name="Oluşturan",
            ),
        ),
        migrations.AddField(
            model_name="dealerpayment",
            name="created_at",
            field=models.DateTimeField(auto_now_add=True, verbose_name="Oluşturulma"),
        ),
        migrations.AddField(
            model_name="dealerpayment",
            name="payment_date_new",
            field=models.DateField(null=True, verbose_name="Ödeme tarihi"),
        ),
        migrations.RunPython(payment_date_to_date, noop),
        migrations.RemoveField(model_name="dealerpayment", name="payment_date"),
        migrations.RenameField(
            model_name="dealerpayment",
            old_name="payment_date_new",
            new_name="payment_date",
        ),
        migrations.AlterField(
            model_name="dealerpayment",
            name="payment_date",
            field=models.DateField(verbose_name="Ödeme tarihi"),
        ),
    ]
