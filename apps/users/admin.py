from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, Admin, RestaurantOwner, Customer


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Admin for the custom User model."""
    list_display = ("username", "email", "first_name", "last_name", "is_active", "created_at")
    search_fields = ("username", "email", "first_name", "last_name", "phone")
    list_filter = ("is_active", "is_staff", "is_superuser", "created_at")
    ordering = ("-created_at",)
    fieldsets = BaseUserAdmin.fieldsets + (
        ("Additional Info", {
            "fields": ("phone", "created_at", "updated_at"),
            "classes": ("collapse",)
        }),
    )
    readonly_fields = ("created_at", "updated_at", "last_login", "date_joined")


@admin.register(Admin)
class AdminProfileAdmin(admin.ModelAdmin):
    """Admin for the Admin profile model."""
    list_display = ("get_username", "title", "created_at")
    search_fields = ("user__username", "user__email", "title")
    list_filter = ("created_at",)
    ordering = ("-created_at",)
    readonly_fields = ("created_at", "updated_at")

    def get_username(self, obj):
        return obj.user.username
    get_username.short_description = "Username"


@admin.register(RestaurantOwner)
class RestaurantOwnerProfileAdmin(admin.ModelAdmin):
    """Admin for the RestaurantOwner profile model."""
    list_display = ("get_username", "business_license", "created_at")
    search_fields = ("user__username", "user__email", "business_license")
    list_filter = ("created_at",)
    ordering = ("-created_at",)
    readonly_fields = ("created_at", "updated_at")

    def get_username(self, obj):
        return obj.user.username
    get_username.short_description = "Username"


@admin.register(Customer)
class CustomerProfileAdmin(admin.ModelAdmin):
    """Admin for the Customer profile model."""
    list_display = ("get_username", "created_at")
    search_fields = ("user__username", "user__email", "dietary_preferences")
    list_filter = ("created_at",)
    ordering = ("-created_at",)
    readonly_fields = ("created_at", "updated_at")

    def get_username(self, obj):
        return obj.user.username
    get_username.short_description = "Username"
