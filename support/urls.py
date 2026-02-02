from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("employee/dashboard/", views.employee_dashboard, name="employee_dashboard"),
    path("employee/ticket/new/", views.raise_ticket, name="raise_ticket"),
    path("employee/ticket/<int:pk>/", views.ticket_detail, name="ticket_detail"),
    path("profile/", views.user_profile, name="user_profile"),
    path("admin/dashboard/", views.admin_dashboard, name="admin_dashboard"),
    path("admin/tickets/<int:pk>/edit/", views.admin_ticket_edit, name="admin_ticket_edit"),
    path("admin/tickets/export/", views.export_tickets_csv, name="export_tickets_csv"),
    path("admin/assets/", views.asset_list, name="asset_list"),
    path("admin/assets/add/", views.asset_add, name="asset_add"),
    path("admin/assets/<int:pk>/edit/", views.asset_edit, name="asset_edit"),
]
