"""
Restaurant URLs (Public + Management)

URL Prefix: /<slug:restaurant_slug>/ (configured in core/urls.py)

PUBLIC RESTAURANT PAGES (Multi-tenant, Slug-Based):
    /<slug>/                        → Public restaurant page & menu
    /<slug>/menu/                   → Full menu view
    /<slug>/about/                  → About restaurant
    /<slug>/contact/                → Contact restaurant
    /<slug>/reserve/                → Make a reservation (requires login)
    /<slug>/gallery/                → Restaurant gallery

OWNER MANAGEMENT (moved to /dashboard/):
    /dashboard/restaurants/         → In apps/dashboard/urls.py
    /dashboard/restaurants/create/
    /dashboard/restaurants/<id>/edit/
    etc.

IMPORTANT:
    Public routes are included LAST in core/urls.py as /<slug>/
    This file contains public-facing restaurant routes only
    Management routes are in dashboard app

Template Usage:
    {% url 'restaurants_public:detail' slug=restaurant.slug %}
    {% url 'restaurants_public:menu' slug=restaurant.slug %}
    {% url 'restaurants_public:reserve' slug=restaurant.slug %}
    {% url 'restaurants_public:about' slug=restaurant.slug %}
"""

from django.urls import path
from . import views

app_name = "restaurants"

urlpatterns = [
    # ========================================================================
    # PUBLIC RESTAURANT PAGES (Multi-Tenant)
    # restaurant_slug is passed from core/urls.py
    # ========================================================================
    path("", views.restaurant_detail, name="detail"),  # Main restaurant page
    path("menu/", views.restaurant_menu, name="menu"),
    path("about/", views.restaurant_about, name="about"),
    path("contact/", views.restaurant_contact, name="contact"),
    path("gallery/", views.restaurant_gallery, name="gallery"),

    # ========================================================================
    # RESERVATION (Public - requires login)
    # Public reservation creation
    # ========================================================================
    path("reserve/", views.create_public_reservation, name="reserve"),
]
