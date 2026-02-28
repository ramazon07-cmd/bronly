"""
Reservation Management URLs

URL Prefix: /reservations/ (configured in core/urls.py)

CUSTOMER Routes:
    /reservations/                  → List my reservations
    /reservations/<id>/             → View reservation details
    /reservations/<id>/cancel/      → Cancel reservation

OWNER Routes:
    /reservations/restaurant/<id>/  → View reservations for specific restaurant
    /reservations/<id>/confirm/     → Confirm pending reservation

IMPORTANT: Public reservation creation happens via:
    /<slug>/reserve/  (in apps/restaurants/public_urls.py)

Template Usage:
    {% url 'reservations:list' %}
    {% url 'reservations:detail' reservation.id %}
    {% url 'reservations:cancel' reservation.id %}
    {% url 'reservations:restaurant' restaurant.id %}
    {% url 'reservations:confirm' reservation.id %}
"""

from django.urls import path
from . import views

app_name = "reservations"

urlpatterns = [
    # ========================================================================
    # CUSTOMER RESERVATION ROUTES
    # ========================================================================
    path("", views.customer_reservations, name="list"),
    path("<int:reservation_id>/", views.reservation_detail, name="detail"),
    path("<int:reservation_id>/cancel/", views.cancel_reservation, name="cancel"),

    # ========================================================================
    # OWNER RESERVATION ROUTES
    # ========================================================================
    path("restaurant/<int:restaurant_id>/", views.restaurant_reservations, name="restaurant"),
    path("<int:reservation_id>/confirm/", views.confirm_reservation, name="confirm"),
    
    # ========================================================================
    # DEPOSIT ROUTES
    # ========================================================================
    path("<int:reservation_id>/deposit/", views.reservation_deposit, name="deposit"),
]
