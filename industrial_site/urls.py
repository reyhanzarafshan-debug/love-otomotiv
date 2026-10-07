"""
URL configuration for industrial_site project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import path, include
from dealer.views import paytr_callback
from public import views as public_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('logout/', auth_views.LogoutView.as_view(next_page='/'), name='logout'),
    path('', public_views.home, name='home'),
    path('products/', public_views.products, name='products'),
    path('categories/', public_views.categories, name='categories'),
    path('cart/', public_views.cart_view, name='cart'),
    path('cart/add/<int:product_id>/', public_views.cart_add, name='cart_add'),
    path('cart/update/', public_views.cart_update, name='cart_update'),
    path('cart/remove/<int:product_id>/', public_views.cart_remove, name='cart_remove'),
    path('checkout/', public_views.checkout, name='checkout'),
    path('order/<int:order_id>/confirm/', public_views.order_confirm, name='order_confirm'),
    path('about/', public_views.about, name='about'),
    path('contact/', public_views.contact, name='contact'),
    path("dealer/", include(("dealer.urls", "dealer"), namespace="dealer")),
    path("payments/paytr/callback/", paytr_callback, name="paytr_callback"),
    path("warehouse/", include("warehouse.urls")),
    path("panel/", include("dashboard.urls")),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
