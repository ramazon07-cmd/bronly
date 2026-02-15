from django.contrib import admin
from .models import Restaurant, Table




class TableInline(admin.TabularInline):
    """Inline editing for tables within restaurant admin."""
    model = Table
    extra = 1
    fields = ("table_number", "capacity", "description", "is_active")


@admin.register(Restaurant)
class RestaurantAdmin(admin.ModelAdmin):
    inlines = [TableInline]
    list_display = ("name", "owner", "city", "cuisine_type", "is_active", "created_at")
    search_fields = ("name", "owner__username", "city", "address")
    list_filter = ("cuisine_type", "is_active", "created_at")
    ordering = ("-created_at",)
    readonly_fields = ("created_at", "updated_at")
    fieldsets = (
        ("Basic Information", {
            "fields": ("owner", "name", "description", "cuisine_type")
        }),
        ("Contact Details", {
            "fields": ("phone", "email", "website")
        }),
        ("Location", {
            "fields": ("address", "city", "postal_code", "latitude", "longitude")
        }),
        ("Operating Hours", {
            "fields": ("opening_time", "closing_time")
        }),
        ("Media", {
            "fields": ("logo", "cover_image")
        }),
        ("Status", {
            "fields": ("is_active",)
        }),
        ("Timestamps", {
            "fields": ("created_at", "updated_at"),
            "classes": ("collapse",)
        }),
    )


@admin.register(Table)
class TableAdmin(admin.ModelAdmin):
    list_display = ("table_number", "restaurant", "capacity", "is_active", "created_at")
    search_fields = ("table_number", "restaurant__name")
    list_filter = ("is_active", "created_at", "restaurant")
    ordering = ("restaurant", "table_number")
    readonly_fields = ("created_at", "updated_at")
    fieldsets = (
        ("Table Information", {
            "fields": ("restaurant", "table_number", "capacity", "description")
        }),
        ("Status", {
            "fields": ("is_active",)
        }),
        ("Timestamps", {
            "fields": ("created_at", "updated_at"),
            "classes": ("collapse",)
        }),
    )
