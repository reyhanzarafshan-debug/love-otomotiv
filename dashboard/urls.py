from django.contrib.admin.views.decorators import staff_member_required
from django.urls import path

from . import views

app_name = "dashboard"

urlpatterns = [
    path("", staff_member_required(views.panel_redirect), name="redirect"),
    path("management/", staff_member_required(views.management_dashboard), name="management"),
    path("warehouse/", staff_member_required(views.warehouse_dashboard), name="warehouse"),
    path("dealer/", staff_member_required(views.dealer_dashboard), name="dealer"),
]
