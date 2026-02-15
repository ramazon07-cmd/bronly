from django.db import models
from django.conf import settings


class Restaurant(models.Model):
    """
    Restaurant model containing restaurant details and business information.
    """
    CUISINE_CHOICES = [
        ("italian", "Italian"),
        ("chinese", "Chinese"),
        ("indian", "Indian"),
        ("mexican", "Mexican"),
        ("japanese", "Japanese"),
        ("french", "French"),
        ("american", "American"),
        ("thai", "Thai"),
        ("korean", "Korean"),
        ("vietnamese", "Vietnamese"),
        ("turkish", "Turkish"),
        ("seafood", "Seafood"),
        ("vegan", "Vegan"),
        ("fusion", "Fusion"),
        ("other", "Other"),
    ]

    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="restaurants"
    )
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    cuisine_type = models.CharField(max_length=20, choices=CUISINE_CHOICES)
    phone = models.CharField(max_length=20)
    email = models.EmailField()
    website = models.URLField(blank=True)
    address = models.TextField()
    city = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=20)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    opening_time = models.TimeField()
    closing_time = models.TimeField()
    is_active = models.BooleanField(default=True)
    logo = models.ImageField(upload_to="restaurant_logos/", blank=True)
    cover_image = models.ImageField(upload_to="restaurant_covers/", blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Restaurant"
        verbose_name_plural = "Restaurants"
        ordering = ["-created_at"]

    def __str__(self):
        return self.name

    def is_owned_by(self, user):
        """Check if user owns this restaurant (has restaurant_owner_profile)."""
        return self.owner_id == user.id and hasattr(user, 'restaurant_owner_profile')


class Table(models.Model):
    """
    Table model for individual tables within a restaurant.
    """
    restaurant = models.ForeignKey(
        Restaurant,
        on_delete=models.CASCADE,
        related_name="tables"
    )
    table_number = models.CharField(max_length=10)
    capacity = models.IntegerField()
    description = models.CharField(max_length=200, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Table"
        verbose_name_plural = "Tables"
        unique_together = ("restaurant", "table_number")
        ordering = ["table_number"]

    def __str__(self):
        return f"Table {self.table_number} - {self.restaurant.name}"
