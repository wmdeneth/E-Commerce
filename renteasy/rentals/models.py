from django.db import models
from django.contrib.auth.models import User


class Feature(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self) -> str:
        return self.name


class Vehicle(models.Model):
    TRANSMISSION_CHOICES = [
        ("automatic", "Automatic"),
        ("manual", "Manual"),
    ]
    FUEL_CHOICES = [
        ("petrol", "Petrol"),
        ("diesel", "Diesel"),
        ("electric", "Electric"),
        ("hybrid", "Hybrid"),
    ]

    name = models.CharField(max_length=150)
    brand = models.CharField(max_length=100, blank=True)
    vehicle_type = models.CharField(max_length=50, default="Sedan")
    year = models.PositiveIntegerField(default=2023)
    transmission = models.CharField(max_length=20, choices=TRANSMISSION_CHOICES, default="automatic")
    fuel_type = models.CharField(max_length=20, choices=FUEL_CHOICES, default="petrol")
    mileage_km = models.PositiveIntegerField(default=0)
    seating_capacity = models.PositiveSmallIntegerField(default=5)

    daily_rate = models.DecimalField(max_digits=10, decimal_places=2)
    weekly_rate = models.DecimalField(max_digits=10, decimal_places=2)
    monthly_rate = models.DecimalField(max_digits=10, decimal_places=2)

    is_available = models.BooleanField(default=True)
    description = models.TextField(blank=True)

    features = models.ManyToManyField(Feature, related_name='vehicles', blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return f"{self.brand} {self.name}".strip()


class VehicleImage(models.Model):
    vehicle = models.ForeignKey(Vehicle, related_name='images', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='vehicles/')

    def __str__(self) -> str:
        return f"Image for {self.vehicle}"


class Booking(models.Model):
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("confirmed", "Confirmed"),
        ("cancelled", "Cancelled"),
        ("completed", "Completed"),
    ]

    user = models.ForeignKey(User, related_name='bookings', on_delete=models.CASCADE)
    vehicle = models.ForeignKey(Vehicle, related_name='bookings', on_delete=models.CASCADE)
    start_date = models.DateField()
    end_date = models.DateField()
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        constraints = [
            models.CheckConstraint(check=models.Q(end_date__gte=models.F('start_date')), name='end_after_start'),
        ]

    def __str__(self) -> str:
        return f"{self.vehicle} booking by {self.user} ({self.start_date} to {self.end_date})"

    @property
    def num_days(self) -> int:
        return (self.end_date - self.start_date).days + 1

    def calculate_amount(self) -> None:
        # Simple daily-rate calculation. Could be extended for weekly/monthly pricing.
        self.total_amount = self.num_days * self.vehicle.daily_rate

    def save(self, *args, **kwargs):
        self.calculate_amount()
        super().save(*args, **kwargs)
