"""
Dashboard URLs (Owner/Customer/Admin Panel)

URL Prefix: /dashboard/ (configured in core/urls.py)

CUSTOMER Routes:
    /dashboard/                     → Customer home
    /dashboard/reservations/        → My reservations (quick view)

OWNER Routes:
    /dashboard/restaurants/         → List my restaurants
    /dashboard/restaurants/create/  → Create new restaurant
    /dashboard/restaurants/<id>/    → View restaurant details
    /dashboard/restaurants/<id>/edit/   → Edit restaurant
    /dashboard/restaurants/<id>/delete/ → Delete restaurant
    /dashboard/restaurants/<id>/tables/ → Manage tables
    /dashboard/analytics/           → View analytics

ADMIN Routes:
    /dashboard/admin/               → Admin overview
    /dashboard/admin/users/         → Manage all users
    /dashboard/admin/restaurants/   → Manage all restaurants
    /dashboard/admin/orders/        → View all orders
    /dashboard/admin/analytics/     → System-wide analytics

Template Usage:
    {% url 'dashboard:customer' %}
    {% url 'dashboard:owner_restaurants' %}
    {% url 'dashboard:owner_create' %}
    {% url 'dashboard:owner_edit' restaurant.id %}
    {% url 'dashboard:admin' %}
"""

from django.urls import path
from . import views
from apps.restaurants import views as restaurant_views

app_name = "dashboard"

urlpatterns = [
    # ========================================================================
    # CUSTOMER DASHBOARD
    # ========================================================================
    path("", views.customer_dashboard, name="customer"),
    path("settings/", views.customer_settings, name="settings"),

    # ========================================================================
    # OWNER DASHBOARD
    # ========================================================================
    # Restaurant Management
    path("restaurants/", views.owner_restaurants, name="owner_restaurants"),
    path("restaurants/create/", restaurant_views.create_restaurant, name="restaurant_create"),
    path("restaurants/<int:restaurant_id>/edit/", restaurant_views.update_restaurant, name="restaurant_update"),
    path("restaurants/<int:restaurant_id>/delete/", restaurant_views.delete_restaurant, name="restaurant_delete"),
    path("restaurants/<int:restaurant_id>/tables/", restaurant_views.list_tables, name="tables_list"),
    path("restaurants/<int:restaurant_id>/tables/create/", restaurant_views.create_table, name="table_create"),
    path("tables/<int:table_id>/edit/", restaurant_views.update_table, name="table_update"),
    path("tables/<int:table_id>/delete/", restaurant_views.delete_table, name="table_delete"),

    # Owner Analytics
    path("analytics/", views.owner_analytics, name="owner_analytics"),

    # ========================================================================
    # ADMIN DASHBOARD
    # ========================================================================
    path("admin/", views.admin_dashboard, name="admin"),
    path("admin/users/", views.admin_users, name="admin_users"),
    path("admin/restaurants/", views.admin_restaurants, name="admin_restaurants"),
    path("admin/orders/", views.admin_orders, name="admin_orders"),
    path("admin/analytics/", views.admin_analytics, name="admin_analytics"),
]
