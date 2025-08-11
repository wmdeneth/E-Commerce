from django.contrib import admin
from .models import Vehicle, Feature, VehicleImage, Booking


class VehicleImageInline(admin.TabularInline):
    model = VehicleImage
    extra = 1


@admin.register(Vehicle)
class VehicleAdmin(admin.ModelAdmin):
    list_display = ("id", "brand", "name", "vehicle_type", "year", "daily_rate", "is_available")
    list_filter = ("vehicle_type", "year", "is_available", "fuel_type", "transmission")
    search_fields = ("name", "brand")
    inlines = [VehicleImageInline]
    filter_horizontal = ("features",)


@admin.register(Feature)
class FeatureAdmin(admin.ModelAdmin):
    search_fields = ("name",)


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ("id", "vehicle", "user", "start_date", "end_date", "total_amount", "status")
    list_filter = ("status", "start_date")
    search_fields = ("vehicle__name", "user__username")
