# Generated for ERP-style receivables ledger (Phase-1 dual-write)

from decimal import Decimal
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("dealer", "0022_merge_20260227_0204"),
    ]

    operations = [
        migrations.CreateModel(
            name="AccountTransaction",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("tx_type", models.CharField(choices=[("DEBIT", "Borç (Alacak)"), ("CREDIT", "Alacak (Ödeme)")], max_length=10, verbose_name="Tür")),
                ("amount", models.DecimalField(decimal_places=2, max_digits=12, verbose_name="Tutar")),
                ("remaining_amount", models.DecimalField(decimal_places=2, default=Decimal("0.00"), help_text="Sadece DEBIT için anlamlı; ödemelerle azalır.", max_digits=12, verbose_name="Kalan tutar")),
                ("due_date", models.DateField(blank=True, null=True, verbose_name="Vade tarihi")),
                ("source", models.CharField(choices=[("ORDER_SHIPPED", "Sipariş kargoya çıktı"), ("PAYMENT", "Ödeme"), ("MANUAL_ADJ", "Manuel düzeltme")], max_length=20, verbose_name="Kaynak")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("dealer", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="transactions", to="dealer.dealerprofile")),
                ("related_order", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="ledger_debits", to="dealer.order")),
                ("related_payment", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="ledger_credits", to="dealer.dealerpayment")),
            ],
            options={
                "verbose_name": "Hesap hareketi",
                "verbose_name_plural": "Hesap hareketleri",
                "ordering": ["-created_at"],
            },
        ),
        migrations.CreateModel(
            name="PaymentAllocation",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("amount", models.DecimalField(decimal_places=2, max_digits=12, verbose_name="Ayrılan tutar")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("debit_tx", models.ForeignKey(limit_choices_to={"tx_type": "DEBIT"}, on_delete=django.db.models.deletion.CASCADE, related_name="allocations_received", to="dealer.accounttransaction")),
                ("payment_tx", models.ForeignKey(limit_choices_to={"tx_type": "CREDIT"}, on_delete=django.db.models.deletion.CASCADE, related_name="allocations", to="dealer.accounttransaction")),
            ],
            options={
                "verbose_name": "Ödeme tahsisi",
                "verbose_name_plural": "Ödeme tahsisleri",
                "ordering": ["created_at"],
            },
        ),
        migrations.AddConstraint(
            model_name="paymentallocation",
            constraint=models.CheckConstraint(condition=models.Q(amount__gt=0), name="payment_allocation_positive"),
        ),
    ]
