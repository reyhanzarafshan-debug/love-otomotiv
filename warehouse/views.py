from django.contrib import messages
from django.contrib.auth import views as auth_views
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_http_methods

from dealer.models import DealerProfile, Order


WAREHOUSE_GROUP_NAME = "Warehouse User"


def warehouse_required(view_func):
    """Sadece Warehouse User grubundaki kullanıcılar erişebilir. Admin paneli görmezler (is_staff=False)."""
    def wrap(request, *args, **kwargs):
        if not request.user.is_authenticated:
            from django.urls import reverse
            return redirect(reverse("warehouse:login") + "?next=" + reverse("warehouse:dashboard"))
        if not request.user.groups.filter(name=WAREHOUSE_GROUP_NAME).exists():
            messages.warning(request, "Bu sayfaya erişim yetkiniz yok.")
            return redirect("warehouse:login")
        return view_func(request, *args, **kwargs)
    return wrap


@require_http_methods(["GET", "POST"])
def warehouse_login_view(request):
    """Depo giriş sayfası. Her zaman login ekranı; giriş yapmış kullanıcı önce logout edilir."""
    from django.contrib.auth import authenticate, login, logout
    from django.contrib.auth.forms import AuthenticationForm

    if request.user.is_authenticated:
        logout(request)

    if request.method == "GET":
        form = AuthenticationForm(request)
        return render(request, "warehouse/login.html", {"form": form}, status=200)

    username = request.POST.get("username", "").strip()
    password = request.POST.get("password", "")
    user = authenticate(request, username=username, password=password)

    if user is None:
        form = AuthenticationForm(request, data=request.POST)
        return render(request, "warehouse/login.html", {"form": form}, status=200)

    login(request, user)

    if not user.groups.filter(name=WAREHOUSE_GROUP_NAME).exists():
        logout(request)
        messages.warning(request, "Bu panele erişim yetkiniz yok (Warehouse User değilsiniz).")
        form = AuthenticationForm(request)
        return render(request, "warehouse/login.html", {"form": form}, status=200)

    return redirect("warehouse:dashboard")


@login_required
def warehouse_logout(request):
    from django.contrib.auth import logout
    logout(request)
    return redirect("warehouse:login")


@warehouse_required
def dashboard(request):
    """Depo ekranı: sipariş listesi, fiyat/tutar yok; durum butonları."""
    orders = Order.objects.select_related("dealer").prefetch_related("items__product").order_by("-created_at")
    return render(request, "warehouse/dashboard.html", {"orders": orders})


@warehouse_required
@require_http_methods(["POST"])
def set_status(request, order_id):
    """Sipariş durumu: Hazırlanıyor (pending), Kargolandı (shipped), İptal (cancelled)."""
    order = get_object_or_404(Order, pk=order_id)
    new_status = (request.POST.get("status") or "").strip().lower()
    if new_status not in ("pending", "shipped", "cancelled"):
        messages.error(request, "Geçersiz durum.")
        return redirect("warehouse:dashboard")

    if new_status == "pending":
        order.status = Order.STATUS_PENDING
        order.save(update_fields=["status"])
        messages.success(request, f"Sipariş #{order.id} Hazırlanıyor olarak güncellendi.")
        return redirect("warehouse:dashboard")

    if new_status == "shipped":
        order.status = Order.STATUS_SHIPPED
        order.save(update_fields=["status"])
        messages.success(request, f"Sipariş #{order.id} Kargolandı olarak işlendi. Stok düşüldü.")
        return redirect("warehouse:dashboard")

    if new_status == "cancelled":
        with transaction.atomic():
            if order.status != Order.STATUS_CANCELLED:
                if order.status not in (Order.STATUS_SHIPPED, Order.STATUS_DELIVERED):
                    for item in order.items.select_related("product").all():
                        p = item.product
                        p.stock_reserved = max(0, (p.stock_reserved or 0) - item.quantity)
                        p.save(update_fields=["stock_reserved"])
                if order.dealer_id:
                    order.dealer.update_finance()
            order.status = Order.STATUS_CANCELLED
            order.save(update_fields=["status"])
        messages.success(request, f"Sipariş #{order.id} iptal edildi, rezerve stok geri eklendi.")
        return redirect("warehouse:dashboard")

    return redirect("warehouse:dashboard")
