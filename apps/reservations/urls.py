from django.urls import path
from . import views


urlpatterns = [
    # Reservation views
    path('tables/<int:table_id>/reserve/', views.create_reservation, name='create_reservation'),
    path('reservations/', views.customer_reservations, name='customer_reservations'),
    path('restaurants/<int:restaurant_id>/reservations/', views.restaurant_reservations, name='restaurant_reservations'),
    path('reservations/<int:reservation_id>/cancel/', views.cancel_reservation, name='cancel_reservation'),
]
