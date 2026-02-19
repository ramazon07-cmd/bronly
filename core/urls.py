"""
BRONLY - Production-Ready SaaS URL Architecture

URL Structure:
    /admin/                          → Django Admin Panel
    /auth/                           → Authentication (login, signup, logout)
    /dashboard/                      → Owner/Customer Dashboard (protected)
    /reservations/                   → Reservation Management
    /<slug:restaurant_slug>/         → Public Restaurant Pages (LAST - Catch-all)
    /                                → Landing Page

Key Principles:
    ✓ Admin panel has highest priority
    ✓ Auth routes are public and quick-accessed
    ✓ Dashboard and reservations are protected routes
    ✓ Restaurant slug routes are LAST to avoid conflicts
    ✓ Each app has clean, modular URLs
    ✓ No duplicate path prefixes in included apps
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView
from apps.restaurants import views as restaurant_views

urlpatterns = [
    # ========================================================================
    # 1. DJANGO ADMIN (Highest Priority)
    # ========================================================================
    path("admin/", admin.site.urls),

    # ========================================================================
    # 2. AUTHENTICATION (Public Routes)
    # /auth/login, /auth/signup, /auth/logout, etc.
    # ========================================================================
    path("auth/", include(("apps.users.urls", "users"), namespace="auth")),

    # ========================================================================
    # 3. DASHBOARD (Protected Routes)
    # /dashboard, /dashboard/restaurants, /dashboard/analytics, etc.
    # ========================================================================
    path("dashboard/", include(("apps.dashboard.urls", "dashboard"), namespace="dashboard")),

    # ========================================================================
    # 4. RESERVATIONS (Protected Routes)
    # /reservations, /reservations/<id>, /reservations/<id>/cancel, etc.
    # ========================================================================
    path("reservations/", include(("apps.reservations.urls", "reservations"), namespace="reservations")),

    # ========================================================================
    # 5. LANDING PAGE (Root)
    # ========================================================================
    path("", TemplateView.as_view(template_name="landing.html"), name="landing"),

    # ========================================================================
    # 6. PUBLIC RESTAURANT LIST
    # ========================================================================
    path("restaurants/", restaurant_views.restaurant_list, name="restaurant_list"),

    # ========================================================================
    # 7. PUBLIC RESTAURANT DETAILS + MENU (MULTI-TENANT BY SLUG)
    # /<slug>/,  /<slug>/menu/, etc - registered with namespace
    # ========================================================================
    path("<slug:restaurant_slug>/", include("apps.restaurants.urls", namespace="restaurants_public")),
]

# ============================================================================
# STATIC & MEDIA FILES (Development only)
# ============================================================================
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
