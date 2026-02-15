from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    """
    Base user model for all user types (Admin, RestaurantOwner, Customer).
    Extends Django's AbstractUser with additional fields.
    """
    phone = models.CharField(max_length=20, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "User"
        verbose_name_plural = "Users"

    def __str__(self):
        return f"{self.get_full_name() or self.username}"

    # Custom related_name to avoid clashes
    groups = models.ManyToManyField(
        'auth.Group',
        blank=True,
        help_text='The groups this user belongs to.',
        related_name='user_groups',
        verbose_name='groups',
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        blank=True,
        help_text='Specific permissions for this user.',
        related_name='user_permissions',
        verbose_name='user permissions',
    )


class Admin(models.Model):
    """Admin user profile."""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='admin_profile')
    title = models.CharField(max_length=100, blank=True, help_text="e.g., Super Admin, Moderator")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Admin"
        verbose_name_plural = "Admins"

    def __str__(self):
        return f"Admin: {self.user.get_full_name() or self.user.username}"


class RestaurantOwner(models.Model):
    """Restaurant owner profile."""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='restaurant_owner_profile')
    business_license = models.CharField(max_length=200, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Restaurant Owner"
        verbose_name_plural = "Restaurant Owners"

    def __str__(self):
        return f"Owner: {self.user.get_full_name() or self.user.username}"


class Customer(models.Model):
    """Customer user profile."""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='customer_profile')
    dietary_preferences = models.TextField(blank=True, help_text="Dietary restrictions, allergies, etc.")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Customer"
        verbose_name_plural = "Customers"

    def __str__(self):
        return f"Customer: {self.user.get_full_name() or self.user.username}"
