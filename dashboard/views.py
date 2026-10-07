from datetime import timedelta
from decimal import Decimal

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import F, Sum
from django.shortcuts import redirect, render
from django.utils import timezone

from dealer.models import AccountTransaction, DealerProfile, Order, OrderItem, Product

from .auth import (
    get_dealer_profile,
    get_panel_redirect_url,
    user_can_dealer_panel,
    user_can_management,
    user_can_warehouse,
)


def _management_required(view_func):
    def wrap(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect("dealer:login")
        if not user_can_management(request.user):
            messages.warning(request, "Bu panele erişim yetkiniz yok.")
            url = get_panel_redirect_url(request.user)
            return redirect(url or "dealer:dashboard")
        return view_func(request, *args, **kwargs)
    return wrap


def _warehouse_required(view_func):
    def wrap(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect("warehouse:login")
        if not user_can_warehouse(request.user):
            messages.warning(request, "Bu panele erişim yetkiniz yok.")
            url = get_panel_redirect_url(request.user)
            return redirect(url or "dealer:dashboard")
        return view_func(request, *args, **kwargs)
    return wrap


def _dealer_panel_login_required(view_func):
    """Only requires login; view handles DealerProfile / is_active branching."""
    def wrap(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect("dealer:login")
        return view_func(request, *args, **kwargs)
    return wrap


@login_required
def panel_redirect(request):
    """Send user to the right dashboard by role."""
    url_name = get_panel_redirect_url(request.user)
    if url_name:
        return redirect(url_name)
    messages.info(request, "Panele erişim yetkiniz yok.")
    return redirect("dealer:dashboard")


@_management_required
def management_dashboard(request):
    today = timezone.now().date()
    month_start = today.replace(day=1)
    next_month = month_start + timedelta(days=32)
    month_end = next_month.replace(day=1) - timedelta(days=1)

    # Exclude cancelled for revenue/counts
    qs = Order.objects.exclude(status=Order.STATUS_CANCELLED)
    today_orders = qs.filter(created_at__date=today)
    month_orders = qs.filter(created_at__date__gte=month_start, created_at__date__lte=month_end)

    today_orders_count = today_orders.count()
    month_orders_count = month_orders.count()

    # Revenue = sum of (quantity * unit_price) for order items in these orders
    today_revenue = (
        OrderItem.objects.filter(order__in=today_orders)
        .aggregate(s=Sum(F("quantity") * F("unit_price")))["s"] or Decimal("0")
    )
    month_revenue = (
        OrderItem.objects.filter(order__in=month_orders)
        .aggregate(s=Sum(F("quantity") * F("unit_price")))["s"] or Decimal("0")
    )

    # Dealer debt
    total_dealer_debt = (
        DealerProfile.objects.aggregate(s=Sum("total_debt"))["s"] or Decimal("0")
    )
    count_dealers_over_limit = DealerProfile.objects.filter(
        total_debt__gt=F("credit_limit")
    ).count()
    count_dealers_with_risk_warning = DealerProfile.objects.filter(
        risk_warning=True
    ).count()

    # Top 5 products by quantity sold (all time, non-cancelled orders)
    order_ids_active = Order.objects.exclude(status=Order.STATUS_CANCELLED).values_list(
        "id", flat=True
    )
    top_5_products_by_quantity = (
        OrderItem.objects.filter(order_id__in=order_ids_active)
        .values("product__id", "product__name", "product__sku")
        .annotate(total_qty=Sum("quantity"))
        .order_by("-total_qty")[:5]
    )

    # Top 5 dealers by revenue (all time, non-cancelled)
    top_5_dealers_by_revenue = (
        Order.objects.filter(dealer__isnull=False)
        .exclude(status=Order.STATUS_CANCELLED)
        .values("dealer__id", "dealer__company_name")
        .annotate(
            revenue=Sum(F("items__quantity") * F("items__unit_price"))
        )
        .order_by("-revenue")[:5]
    )

    # Management summary
    total_dealers = DealerProfile.objects.count()
    all_orders = Order.objects.exclude(status=Order.STATUS_CANCELLED)
    total_orders = all_orders.count()
    total_revenue = (
        OrderItem.objects.filter(order__in=all_orders)
        .aggregate(s=Sum(F("quantity") * F("unit_price")))["s"] or Decimal("0")
    )
    stock_summary = Product.objects.aggregate(
        total_on_hand=Sum("stock_on_hand"),
        total_reserved=Sum("stock_reserved"),
    )
    stock_summary["total_on_hand"] = stock_summary["total_on_hand"] or 0
    stock_summary["total_reserved"] = stock_summary["total_reserved"] or 0
    stock_summary["product_count"] = Product.objects.filter(is_active=True).count()
    recent_orders = (
        Order.objects.exclude(status=Order.STATUS_CANCELLED)
        .select_related("dealer")
        .prefetch_related("items__product")
        .order_by("-created_at")[:20]
    )

    context = {
        "page_title": "Panel Management",
        "today_orders_count": today_orders_count,
        "today_revenue": today_revenue,
        "month_orders_count": month_orders_count,
        "month_revenue": month_revenue,
        "total_dealers": total_dealers,
        "total_orders": total_orders,
        "total_revenue": total_revenue,
        "stock_summary": stock_summary,
        "recent_orders": recent_orders,
        "total_dealer_debt": total_dealer_debt,
        "count_dealers_over_limit": count_dealers_over_limit,
        "count_dealers_with_risk_warning": count_dealers_with_risk_warning,
        "top_5_products_by_quantity": top_5_products_by_quantity,
        "top_5_dealers_by_revenue": top_5_dealers_by_revenue,
    }
    return render(request, "dashboard/management.html", context)


@_warehouse_required
def warehouse_dashboard(request):
    today = timezone.now().date()

    # Orders: pending = to prepare, approved = ready to ship (we don't have "preparing" status)
    orders_to_prepare = Order.objects.filter(status=Order.STATUS_PENDING).exclude(
        status=Order.STATUS_CANCELLED
    )
    orders_preparing = Order.objects.filter(status=Order.STATUS_APPROVED)
    orders_ready_to_ship = Order.objects.filter(status=Order.STATUS_APPROVED)
    today_shipments_count = Order.objects.filter(
        status=Order.STATUS_SHIPPED, updated_at__date=today
    ).count()

    # Low stock: (stock_on_hand - stock_reserved) <= threshold
    LOW_STOCK_THRESHOLD = 5
    low_stock_products = (
        Product.objects.filter(is_active=True)
        .annotate(available=F("stock_on_hand") - F("stock_reserved"))
        .filter(available__lte=LOW_STOCK_THRESHOLD)
        .order_by("available")[:20]
    )

    context = {
        "page_title": "Panel Management",
        "orders_to_prepare": orders_to_prepare.select_related("dealer").prefetch_related(
            "items__product"
        )[:50],
        "orders_preparing": orders_preparing.select_related("dealer").prefetch_related(
            "items__product"
        )[:50],
        "orders_ready_to_ship": orders_ready_to_ship.select_related(
            "dealer"
        ).prefetch_related("items__product")[:50],
        "orders_to_prepare_count": orders_to_prepare.count(),
        "orders_preparing_count": orders_preparing.count(),
        "orders_ready_to_ship_count": orders_ready_to_ship.count(),
        "today_shipments_count": today_shipments_count,
        "low_stock_products": low_stock_products,
        "low_stock_threshold": LOW_STOCK_THRESHOLD,
    }
    return render(request, "dashboard/warehouse.html", context)


@_dealer_panel_login_required
def dealer_dashboard(request):
    profile = get_dealer_profile(request.user)
    if not profile:
        return render(
            request,
            "dashboard/dealer_message.html",
            {"page_title": "Panel Management", "message": "This account is not linked to a dealer. Contact admin."},
        )
    if not profile.is_active:
        return render(
            request,
            "dashboard/dealer_message.html",
            {"page_title": "Panel Management", "message": "Your dealer account is waiting approval."},
        )
    profile.update_lock()
    profile.refresh_from_db()

    remaining = profile.remaining_credit
    has_warning = (remaining is not None and remaining < 0) or profile.risk_warning

    open_orders = (
        profile.orders.exclude(status=Order.STATUS_CANCELLED)
        .exclude(status=Order.STATUS_SHIPPED)
        .exclude(status=Order.STATUS_DELIVERED)
        .order_by("-created_at")
    )
    last_8_orders = profile.orders.exclude(status=Order.STATUS_CANCELLED).order_by(
        "-created_at"
    )[:8]
    pending_orders = profile.orders.filter(status=Order.STATUS_PENDING).order_by("-created_at")
    pending_orders_count = pending_orders.count()
    pending_orders_total = pending_orders.aggregate(s=Sum("total_amount"))["s"] or Decimal("0.00")
    ledger_entries = profile.transactions.select_related("related_order", "related_payment").order_by("-created_at")[:8]

    is_risky = profile._is_risky_for_order()
    total_payments = profile.payments.aggregate(s=Sum("amount"))["s"] or 0
    payment_history = profile.payments.select_related("created_by").order_by("-payment_date", "-created_at")[:8]
    available_limit = profile.remaining_credit
    credit_limit = profile.credit_limit or 0
    current_debt = profile.current_debt or 0
    limit_exceeded = current_debt >= credit_limit
    usage_percent = (float(current_debt) / float(credit_limit) * 100) if credit_limit else 0
    usage_percent_display = round(usage_percent, 1)
    usage_percent_bar = min(100, usage_percent_display)
    context = {
        "page_title": "Panel Management — Bayiler",
        "profile": profile,
        "remaining_limit": available_limit,
        "available_limit": available_limit,
        "total_payments": total_payments,
        "has_warning": has_warning,
        "is_order_blocked": profile.is_order_blocked,
        "order_block_override": profile.order_block_override,
        "is_risky": is_risky,
        "limit_exceeded": limit_exceeded,
        "usage_percent": usage_percent_bar,
        "usage_percent_display": usage_percent_display,
        "open_orders": open_orders.prefetch_related("items__product"),
        "last_8_orders": last_8_orders.prefetch_related("items__product"),
        "last_10_orders": last_8_orders.prefetch_related("items__product"),
        "payment_history": payment_history,
        "ledger_entries": ledger_entries,
        "pending_orders": pending_orders.prefetch_related("items__product")[:8],
        "pending_orders_count": pending_orders_count,
        "pending_orders_total": pending_orders_total,
    }
    return render(request, "dashboard/dealer.html", context)


def dashboard_nav_context(request):
    """Context for top nav: which panels this user can see."""
    if not request.user.is_authenticated:
        return {"dashboard_can_management": False, "dashboard_can_warehouse": False, "dashboard_can_dealer": False, "dashboard_panel_url": None}
    return {
        "dashboard_can_management": user_can_management(request.user),
        "dashboard_can_warehouse": user_can_warehouse(request.user),
        "dashboard_can_dealer": user_can_dealer_panel(request.user),
        "dashboard_panel_url": get_panel_redirect_url(request.user),
    }
