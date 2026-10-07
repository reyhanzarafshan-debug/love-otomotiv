import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from django import forms
from django.contrib import admin
from django.contrib import messages
from django.db import transaction
from django.http import HttpResponseRedirect
from django.utils.safestring import mark_safe

from dealer.models import (
    AccountTransaction,
    BankTransferNotice,
    Category,
    DealerPayment,
    DealerProfile,
    MailOrderRequest,
    OnlinePaymentRequest,
    Order,
    OrderItem,
    PaymentAllocation,
    Product,
)


class OrderItemInlineForm(forms.ModelForm):
    """unit_price read-only unless manual_price_override is checked."""

    class Meta:
        model = OrderItem
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not getattr(self.instance, "manual_price_override", False):
            self.fields["unit_price"].widget.attrs["readonly"] = True
            self.fields["unit_price"].widget.attrs["style"] = "background-color: #f0f0f0;"


def format_decimal(value):
    """Safe decimal formatting for admin list display; no format_html."""
    if value is None:
        return "0 ₺"
    try:
        return f"{float(value):,.2f} ₺"
    except (TypeError, ValueError):
        return "0 ₺"


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "slug")
    prepopulated_fields = {"slug": ("name",)}


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "sku",
        "category",
        "price",
        "price_a",
        "price_b",
        "price_c",
        "retail_price",
        "dealer_price",
        "stock_on_hand",
        "stock_reserved",
        "available_stock_display",
        "is_active",
    )
    list_filter = ("is_active", "category")
    search_fields = ("name", "sku")
    readonly_fields = ("available_stock_display",)
    fieldsets = (
        (None, {"fields": ("name", "sku", "description", "category", "image", "is_active")}),
        (
            "Fiyat",
            {
                "fields": (
                    "price",
                    "price_a",
                    "price_b",
                    "price_c",
                    "retail_price",
                    "dealer_price",
                ),
            },
        ),
        ("Stok", {"fields": ("stock_on_hand", "stock_reserved", "available_stock_display")}),
    )

    def available_stock_display(self, obj):
        return obj.available_stock
    available_stock_display.short_description = "Satılabilir stok"


@admin.register(DealerProfile)
class DealerProfileAdmin(admin.ModelAdmin):
    list_display = (
        "company_name",
        "contact_person",
        "phone",
        "email",
        "credit_limit_display",
        "current_debt_display",
        "risk_status_display",
        "order_block_status_display",
        "order_block_override",
        "payment_term_days",
        "is_active",
        "risk_warning",
        "is_approved",
        "is_locked",
        "created_at",
    )
    list_display_links = ("company_name",)
    list_filter = ("is_active", "is_approved", "is_locked", "risk_warning", "order_block_override")
    search_fields = (
        "company_name",
        "contact_person",
        "phone",
        "email",
        "tax_number",
        "user__username",
        "user__email",
    )
    readonly_fields = ("total_debt", "remaining_credit", "is_locked", "created_at")
    list_editable = ("is_active", "risk_warning", "is_approved", "order_block_override")
    list_per_page = 25
    date_hierarchy = "created_at"
    fieldsets = (
        (
            "Account",
            {"fields": ("user", "price_level", "is_approved", "is_active", "is_locked", "risk_warning", "order_block_override")},
        ),
        (
            "Company",
            {
                "fields": (
                    "company_name",
                    "contact_person",
                    "phone",
                    "email",
                    "address",
                    "tax_number",
                ),
            },
        ),
        (
            "Finance",
            {
                "fields": (
                    "credit_limit",
                    "current_debt",
                    "total_debt",
                    "remaining_credit",
                    "payment_term_days",
                    "last_due_date",
                ),
            },
        ),
        ("Dates", {"fields": ("created_at",)}),
    )
    autocomplete_fields = ("user",)

    def credit_limit_display(self, obj):
        return format_decimal(obj.credit_limit if obj else None)
    credit_limit_display.short_description = "Credit limit"

    def current_debt_display(self, obj):
        return format_decimal(obj.current_debt if obj else None)
    current_debt_display.short_description = "Current debt"

    def risk_status_display(self, obj):
        over = obj.is_over_credit_limit
        flagged = obj.risk_warning
        if over and flagged:
            return mark_safe(
                '<span style="color: #b71c1c; font-weight: bold;">⚠ Over limit + Risk</span>'
            )
        if over:
            return mark_safe(
                '<span style="color: #b71c1c; font-weight: bold;">⚠ Over limit</span>'
            )
        if flagged:
            return mark_safe('<span style="color: #e65100;">Risk flagged</span>')
        return mark_safe('<span style="color: #2e7d32;">✓ OK</span>')
    risk_status_display.short_description = "Risk status"

    def order_block_status_display(self, obj):
        if obj.order_block_override and obj._is_risky_for_order():
            return mark_safe('<span style="color: #1565c0;">Allowed (override)</span>')
        if obj.is_order_blocked:
            return mark_safe('<span style="color: #b71c1c; font-weight: bold;">Blocked</span>')
        return mark_safe('<span style="color: #2e7d32;">Allowed</span>')
    order_block_status_display.short_description = "Order block"


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    form = OrderItemInlineForm
    extra = 1
    min_num = 0
    readonly_fields = ("line_total",)
    fields = ("product", "quantity", "manual_price_override", "unit_price", "line_total")
    verbose_name = "Sipariş kalemi"
    verbose_name_plural = "Sipariş kalemleri"
    autocomplete_fields = ("product",)


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("id", "order_type", "order_source", "customer_or_dealer", "status", "total_amount", "due_date", "created_at", "updated_at")
    list_filter = ("status", "order_source", "created_at")
    search_fields = ("customer_name", "customer_email", "dealer__company_name", "dealer__user__username")
    inlines = [OrderItemInline]
    readonly_fields = ("created_at", "updated_at", "total_amount")
    fieldsets = (
        (
            None,
            {
                "fields": ("dealer", "order_source", "status", "due_date", "total_amount"),
                "description": "Toplam tutar, sipariş kalemleri eklenip kaydedildikçe otomatik güncellenir.",
            },
        ),
        ("Misafir müşteri (dealer boşsa)", {"fields": ("customer_name", "customer_phone", "customer_email")}),
        ("Adres ve not", {"fields": ("delivery_address", "order_notes")}),
        ("Tarihler", {"fields": ("created_at", "updated_at")}),
    )
    actions = ["cancel_orders_restore_stock"]

    def order_type(self, obj):
        return "Bayi" if obj.dealer_id else "Misafir"
    order_type.short_description = "Tip"

    def customer_or_dealer(self, obj):
        if obj.dealer_id:
            return obj.dealer.company_name
        return obj.customer_name or obj.customer_email or "—"
    customer_or_dealer.short_description = "Müşteri / Bayi"

    @admin.action(description="Seçili siparişleri iptal et (rezerve stok geri eklenir)")
    def cancel_orders_restore_stock(self, request, queryset):
        with transaction.atomic():
            dealers_to_update = set()
            for order in queryset.exclude(status=Order.STATUS_CANCELLED):
                if order.status not in (Order.STATUS_SHIPPED, Order.STATUS_DELIVERED):
                    for item in order.items.select_related("product").all():
                        p = item.product
                        p.stock_reserved = max(0, (p.stock_reserved or 0) - item.quantity)
                        p.save(update_fields=["stock_reserved"])
                if order.dealer_id:
                    dealers_to_update.add(order.dealer_id)
                order.status = Order.STATUS_CANCELLED
                order.save(update_fields=["status"])
            for dealer in DealerProfile.objects.filter(pk__in=dealers_to_update):
                dealer.update_finance()
        self.message_user(request, f"{queryset.count()} sipariş iptal edildi, rezerve stoklar güncellendi.", messages.SUCCESS)
        return HttpResponseRedirect(request.get_full_path())

    def save_model(self, request, obj, form, change):
        if change:
            old = Order.objects.filter(pk=obj.pk).first()
            if old and old.status != Order.STATUS_CANCELLED and obj.status == Order.STATUS_CANCELLED:
                if old.status not in (Order.STATUS_SHIPPED, Order.STATUS_DELIVERED):
                    with transaction.atomic():
                        for item in obj.items.select_related("product").all():
                            p = item.product
                            p.stock_reserved = max(0, (p.stock_reserved or 0) - item.quantity)
                            p.save(update_fields=["stock_reserved"])
                if obj.dealer_id:
                    obj.dealer.update_finance()
        super().save_model(request, obj, form, change)

    def save_related(self, request, form, formsets, change):
        super().save_related(request, form, formsets, change)
        if form.instance.pk:
            form.instance.recalculate_totals()


@admin.register(DealerPayment)
class DealerPaymentAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "dealer",
        "amount",
        "payment_method",
        "payment_date",
        "status",
        "description_short",
        "created_by",
        "created_at",
    )
    list_filter = ("dealer", "payment_method", "status", "payment_date", "created_by")
    search_fields = ("dealer__company_name", "description", "note")
    readonly_fields = ("created_at",)
    autocomplete_fields = ("dealer", "created_by")
    date_hierarchy = "payment_date"
    list_per_page = 25
    list_editable = ("status",)

    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        from django.db.models import Sum
        qs = self.get_queryset(request)
        dealer_id = request.GET.get("dealer__id__exact") or request.GET.get("dealer")
        if dealer_id:
            total = qs.filter(dealer_id=dealer_id).aggregate(s=Sum("amount"))["s"] or 0
            extra_context["dealer_payments_total"] = total
        return super().changelist_view(request, extra_context=extra_context)

    def save_model(self, request, obj, form, change):
        if not change and not obj.created_by_id:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)
        # Borç güncellemesi DealerPayment.save() içinde transaction + incremental delta ile yapılıyor

    def description_short(self, obj):
        if not obj.description:
            return "—"
        return obj.description[:60] + ("..." if len(obj.description) > 60 else "")

    description_short.short_description = "Açıklama"


@admin.register(AccountTransaction)
class AccountTransactionAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "dealer",
        "tx_type",
        "amount",
        "remaining_amount",
        "due_date_display",
        "source",
        "related_order_display",
        "related_payment_display",
        "created_at",
    )
    list_filter = ("tx_type", "source", "dealer")
    search_fields = ("dealer__company_name",)
    readonly_fields = ("created_at", "updated_at")
    raw_id_fields = ("related_order", "related_payment")
    date_hierarchy = "created_at"
    list_per_page = 50

    def due_date_display(self, obj):
        if obj.tx_type == AccountTransaction.TX_CREDIT:
            return "—"
        return obj.due_date or "—"
    due_date_display.short_description = "Vade"
    due_date_display.admin_order_field = "due_date"

    def related_order_display(self, obj):
        if obj.tx_type == AccountTransaction.TX_CREDIT:
            return "—"
        return obj.related_order or "—"
    related_order_display.short_description = "İlgili sipariş"

    def related_payment_display(self, obj):
        if obj.tx_type == AccountTransaction.TX_DEBIT:
            return "—"
        return obj.related_payment or "—"
    related_payment_display.short_description = "İlgili ödeme"


@admin.register(PaymentAllocation)
class PaymentAllocationAdmin(admin.ModelAdmin):
    list_display = ("id", "payment", "payment_tx", "debit_tx", "amount", "created_at")
    list_filter = ("payment_tx__dealer",)
    readonly_fields = ("created_at",)
    raw_id_fields = ("payment", "payment_tx", "debit_tx")
    list_per_page = 50


@admin.register(MailOrderRequest)
class MailOrderRequestAdmin(admin.ModelAdmin):
    list_display = ("id", "dealer", "amount", "status", "phone", "created_at", "approved_at", "approved_by")
    list_filter = ("status", "dealer", "created_at")
    search_fields = ("dealer__company_name", "note", "phone")
    readonly_fields = ("created_at", "updated_at", "approved_at")
    list_per_page = 25
    date_hierarchy = "created_at"
    actions = ["mark_approved", "mark_rejected"]

    @admin.action(description="Seçilileri onayla")
    def mark_approved(self, request, queryset):
        from django.utils import timezone
        updated = queryset.exclude(status=MailOrderRequest.STATUS_APPROVED).update(
            status=MailOrderRequest.STATUS_APPROVED,
            approved_at=timezone.now(),
            approved_by_id=request.user.id,
        )
        self.message_user(request, f"{updated} talep onaylandı.", messages.SUCCESS)

    @admin.action(description="Seçilileri reddet")
    def mark_rejected(self, request, queryset):
        updated = queryset.exclude(status=MailOrderRequest.STATUS_REJECTED).update(
            status=MailOrderRequest.STATUS_REJECTED,
        )
        self.message_user(request, f"{updated} talep reddedildi.", messages.SUCCESS)


@admin.register(BankTransferNotice)
class BankTransferNoticeAdmin(admin.ModelAdmin):
    list_display = ("id", "dealer", "amount", "transfer_date", "status", "created_at")
    list_filter = ("status", "dealer", "created_at")
    search_fields = ("dealer__company_name", "note")
    readonly_fields = ("created_at", "updated_at", "approved_at")
    list_per_page = 25
    date_hierarchy = "created_at"
    actions = ["mark_approved", "mark_rejected"]
    autocomplete_fields = ("dealer", "approved_by", "related_payment")

    @admin.action(description="Seçilileri onayla")
    def mark_approved(self, request, queryset):
        from django.utils import timezone
        to_approve = queryset.exclude(status=BankTransferNotice.STATUS_APPROVED)
        count = to_approve.count()
        for notice in to_approve:
            notice.status = BankTransferNotice.STATUS_APPROVED
            notice.approved_at = timezone.now()
            notice.approved_by = request.user
            notice.save()
        if count:
            self.message_user(request, f"{count} bildirim onaylandı.", messages.SUCCESS)

    @admin.action(description="Seçilileri reddet")
    def mark_rejected(self, request, queryset):
        updated = queryset.exclude(status=BankTransferNotice.STATUS_REJECTED).update(
            status=BankTransferNotice.STATUS_REJECTED,
        )
        self.message_user(request, f"{updated} bildirim reddedildi.", messages.SUCCESS)


@admin.register(OnlinePaymentRequest)
class OnlinePaymentRequestAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "dealer",
        "amount",
        "merchant_oid",
        "status",
        "payment_date",
        "related_payment",
        "created_at",
    )
    list_filter = ("status", "provider", "dealer", "created_at")
    search_fields = ("merchant_oid", "dealer__company_name")
    readonly_fields = ("created_at", "updated_at", "callback_payload")
    list_per_page = 25
    date_hierarchy = "created_at"
    raw_id_fields = ("related_payment",)
    autocomplete_fields = ("dealer",)
