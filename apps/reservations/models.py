from django.db import models
from django.conf import settings
from apps.restaurants.models import Table


class Reservation(models.Model):
    """
    Reservation model for table bookings at restaurants.
    """
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('cancelled', 'Cancelled'),
        ('completed', 'Completed'),
    ]

    customer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="reservations"
    )
    table = models.ForeignKey(
        Table,
        on_delete=models.CASCADE,
        related_name="reservations"
    )
    reservation_date = models.DateField()
    reservation_time = models.TimeField()
    guest_count = models.IntegerField()
    special_requests = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Reservation"
        verbose_name_plural = "Reservations"
        ordering = ["-reservation_date", "-reservation_time"]

    def __str__(self):
        return f"Reservation - {self.customer} at {self.table.restaurant.name} on {self.reservation_date}"

    @property
    def restaurant(self):
        """Get the restaurant from the table."""
        return self.table.restaurant
