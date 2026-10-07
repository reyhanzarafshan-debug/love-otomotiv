from django.urls import path

from . import views

app_name = "warehouse"

urlpatterns = [
    path("login/", views.warehouse_login_view, name="login"),
    path("logout/", views.warehouse_logout, name="logout"),
    path("", views.dashboard, name="dashboard"),
    path("order/<int:order_id>/status/", views.set_status, name="set_status"),
]
