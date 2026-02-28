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
        ('no_show', 'No Show'),
    ]

    DEPOSIT_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('paid', 'Paid'),
        ('refunded', 'Refunded'),
        ('partially_refunded', 'Partially Refunded'),
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
    
    # Deposit fields
    deposit_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    deposit_status = models.CharField(max_length=20, choices=DEPOSIT_STATUS_CHOICES, default='pending')
    arrival_confirmed = models.BooleanField(default=False)
    
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
    
    def get_time_range(self, duration_hours=2):
        """Get the time range for conflict detection (default 2-hour window)."""
        from datetime import datetime, timedelta
        
        # Combine date and time
        reservation_datetime = datetime.combine(self.reservation_date, self.reservation_time)
        
        # Create time range (reservation_time to reservation_time + duration)
        start_time = reservation_datetime
        end_time = reservation_datetime + timedelta(hours=duration_hours)
        
        return start_time, end_time
