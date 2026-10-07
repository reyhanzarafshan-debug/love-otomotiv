from django.contrib import messages
from django.db import transaction
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.decorators.http import require_http_methods

from core.models import SiteSettings
from dealer.models import Category, Order, OrderItem, Product
from .forms import ContactForm, GuestCheckoutForm

CART_SESSION_KEY = "cart"


def _get_cart(request):
    return request.session.get(CART_SESSION_KEY) or {}


def _set_cart(request, cart):
    request.session[CART_SESSION_KEY] = cart
    request.session.modified = True


def _get_cart_items_and_total(request):
    """Session cart'tan cart_items ve total döner (checkout ve cart aynı kaynak)."""
    cart = _get_cart(request)
    product_ids = list(cart.keys())
    products_list = Product.objects.filter(pk__in=product_ids, is_active=True)
    product_map = {str(p.id): p for p in products_list}
    cart_items = []
    for pid, qty in cart.items():
        if pid not in product_map:
            continue
        try:
            qty = int(qty)
        except (TypeError, ValueError):
            qty = 1
        qty = max(1, qty)
        p = product_map[pid]
        unit_price = p.retail_price
        line_total = unit_price * qty
        cart_items.append({
            "product": p,
            "quantity": qty,
            "unit_price": unit_price,
            "line_total": line_total,
        })
    total = sum(c["line_total"] for c in cart_items)
    return cart_items, total


def home(request):
    categories = Category.objects.all()[:6]
    products = Product.objects.filter(is_active=True).select_related("category")[:8]
    return render(
        request,
        "public/home.html",
        {"categories": categories, "products": products},
    )


def categories(request):
    categories_list = Category.objects.all()
    return render(request, "public/categories.html", {"categories": categories_list})


def products(request):
    products_qs = Product.objects.filter(is_active=True).select_related("category")
    q = request.GET.get("q", "").strip()
    if q:
        products_qs = products_qs.filter(
            Q(name__icontains=q) | Q(sku__icontains=q) | Q(description__icontains=q)
        )
    cat_slug = request.GET.get("category", "").strip()
    if cat_slug:
        products_qs = products_qs.filter(category__slug=cat_slug)
    categories_list = Category.objects.all()
    return render(
        request,
        "public/products.html",
        {"products": products_qs, "categories": categories_list, "q": q, "cat_slug": cat_slug},
    )


def cart_view(request):
    cart_items, total = _get_cart_items_and_total(request)
    return render(request, "public/cart.html", {"cart_items": cart_items, "total": total})


@require_http_methods(["POST"])
def cart_add(request, product_id):
    product = get_object_or_404(Product, pk=product_id, is_active=True)
    try:
        quantity = int(request.POST.get("quantity", 1))
        quantity = max(1, min(quantity, product.available_stock or 999))
    except (ValueError, TypeError):
        quantity = 1
    cart = _get_cart(request)
    key = str(product_id)
    cart[key] = cart.get(key, 0) + quantity
    _set_cart(request, cart)
    messages.success(request, f"'{product.name}' sepete eklendi.")
    next_url = request.POST.get("next") or request.META.get("HTTP_REFERER") or reverse("products")
    return redirect(next_url)


@require_http_methods(["POST"])
def cart_update(request):
    cart = _get_cart(request)
    new_cart = {}
    for key in list(cart.keys()):
        # Template: name="quantity_{{ item.product.id }}" -> quantity_5, key session'da "5"
        qty_val = request.POST.get("quantity_" + str(key))
        if qty_val is None:
            new_cart[key] = cart[key]
            continue
        try:
            qty = int(qty_val)
            if qty <= 0:
                continue
            new_cart[key] = qty
        except (ValueError, TypeError):
            new_cart[key] = cart[key]
    request.session[CART_SESSION_KEY] = new_cart
    request.session.modified = True
    messages.success(request, "Sepet güncellendi.")
    return redirect("cart")


@require_http_methods(["POST"])
def cart_remove(request, product_id):
    cart = _get_cart(request)
    cart.pop(str(product_id), None)
    _set_cart(request, cart)
    messages.success(request, "Ürün sepetten çıkarıldı.")
    return redirect("cart")


def checkout(request):
    cart_items, total = _get_cart_items_and_total(request)
    if not cart_items:
        messages.warning(request, "Sepetiniz boş.")
        return redirect("products")

    if request.method == "POST":
        form = GuestCheckoutForm(request.POST)
        if form.is_valid():
            try:
                with transaction.atomic():
                    # Stok kontrolü ve kilitleme (race condition önleme)
                    product_ids = [c["product"].id for c in cart_items]
                    products_locked = Product.objects.select_for_update().filter(
                        pk__in=product_ids, is_active=True
                    )
                    product_by_id = {p.id: p for p in products_locked}
                    insufficient = []
                    for c in cart_items:
                        pid, qty = c["product"].id, c["quantity"]
                        if pid not in product_by_id:
                            continue
                        p = product_by_id[pid]
                        if p.available_stock < qty:
                            insufficient.append(f"{p.name}: müsait stok {p.available_stock}, istemeniz {qty}")
                    if insufficient:
                        messages.error(
                            request,
                            "Stok yetersiz: " + "; ".join(insufficient) + ". Sipariş oluşturulmadı.",
                        )
                        return render(
                            request,
                            "public/checkout.html",
                            {"form": form, "cart_items": cart_items, "total": total},
                        )
                    # Rezerve stok artır, sipariş oluştur (stock_on_hand değişmez)
                    for c in cart_items:
                        p = product_by_id[c["product"].id]
                        p.stock_reserved = (p.stock_reserved or 0) + c["quantity"]
                        p.save(update_fields=["stock_reserved"])
                    order = Order.objects.create(
                        dealer=None,
                        status=Order.STATUS_PENDING,
                        order_source=Order.SOURCE_ONLINE,
                        customer_name=form.cleaned_data["customer_name"],
                        customer_phone=form.cleaned_data["customer_phone"],
                        customer_email=form.cleaned_data["customer_email"],
                        delivery_address=form.cleaned_data["delivery_address"],
                        order_notes=form.cleaned_data.get("order_notes", ""),
                    )
                    for c in cart_items:
                        OrderItem.objects.create(
                            order=order,
                            product=product_by_id[c["product"].id],
                            quantity=int(c["quantity"]),
                            unit_price=c["unit_price"],
                        )
                    _set_cart(request, {})
                    return redirect(reverse("order_confirm", args=[order.id]))
            except Exception:
                messages.error(request, "Sipariş oluşturulurken bir hata oluştu. Lütfen tekrar deneyin.")
                return render(
                    request,
                    "public/checkout.html",
                    {"form": form, "cart_items": cart_items, "total": total},
                )
    else:
        form = GuestCheckoutForm()
    return render(
        request,
        "public/checkout.html",
        {"form": form, "cart_items": cart_items, "total": total},
    )


def order_confirm(request, order_id):
    order = get_object_or_404(Order, pk=order_id)
    if order.dealer_id is not None:
        messages.warning(request, "Bu sipariş bayi siparişidir.")
        return redirect("home")
    return render(request, "public/order_confirm.html", {"order": order})


def about(request):
    return render(request, "public/about.html")


def contact(request):
    form = ContactForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        messages.success(request, "Mesajınız alındı. En kısa sürede size dönüş yapacağız.")
        return redirect("contact")
    settings = SiteSettings.get()
    # WhatsApp her zaman 0551 401 40 41 (212 numara kullanılmaz)
    raw = "".join(c for c in (settings.phone or "") if c.isdigit())
    if raw and not raw.startswith("90"):
        raw = "90" + raw.lstrip("0")
    if not raw or "212" in (settings.phone or ""):
        raw = "905514014041"
    whatsapp_number = raw
    return render(
        request,
        "public/contact.html",
        {"form": form, "whatsapp_number": whatsapp_number},
    )
