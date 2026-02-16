from django.contrib import admin
from .models import Reservation


@admin.register(Reservation)
class ReservationAdmin(admin.ModelAdmin):
    list_display = ("customer", "restaurant", "table", "reservation_date", "reservation_time", "status", "created_at")
    search_fields = ("customer__username", "table__restaurant__name")
    list_filter = ("status", "reservation_date", "created_at")
    ordering = ("-reservation_date", "-reservation_time")
    readonly_fields = ("created_at", "updated_at")
    fieldsets = (
        ("Reservation Information", {
            "fields": ("customer", "table", "reservation_date", "reservation_time", "guest_count")
        }),
        ("Special Requests", {
            "fields": ("special_requests",)
        }),
        ("Status", {
            "fields": ("status",)
        }),
        ("Timestamps", {
            "fields": ("created_at", "updated_at"),
            "classes": ("collapse",)
        }),
    )
