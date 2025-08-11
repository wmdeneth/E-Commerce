from datetime import date
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Q

from .models import Vehicle, Booking
from .forms import UserRegistrationForm, BookingForm


def home(request):
    latest_vehicles = Vehicle.objects.order_by('-created_at')[:6]
    return render(request, 'home.html', {"vehicles": latest_vehicles})


def vehicle_list(request):
    query = request.GET.get('q', '').strip()
    vehicles = Vehicle.objects.filter(is_available=True)
    if query:
        vehicles = vehicles.filter(Q(name__icontains=query) | Q(brand__icontains=query) | Q(vehicle_type__icontains=query))
    return render(request, 'rentals/vehicle_list.html', {"vehicles": vehicles, "query": query})


def vehicle_detail(request, pk: int):
    vehicle = get_object_or_404(Vehicle, pk=pk)
    form = BookingForm()
    return render(request, 'rentals/vehicle_detail.html', {"vehicle": vehicle, "form": form})


@login_required
def book_vehicle(request, pk: int):
    vehicle = get_object_or_404(Vehicle, pk=pk)
    if request.method == 'POST':
        form = BookingForm(request.POST)
        if form.is_valid():
            start_date = form.cleaned_data['start_date']
            end_date = form.cleaned_data['end_date']
            if end_date < start_date:
                messages.error(request, 'End date must be after start date')
                return redirect('vehicle_detail', pk=vehicle.pk)
            # Prevent overlaps
            overlap = Booking.objects.filter(
                vehicle=vehicle,
                status__in=['pending', 'confirmed', 'completed'],
            ).filter(
                Q(start_date__lte=end_date) & Q(end_date__gte=start_date)
            ).exists()
            if overlap:
                messages.error(request, 'Vehicle is not available for the selected dates')
                return redirect('vehicle_detail', pk=vehicle.pk)
            booking = Booking.objects.create(
                user=request.user,
                vehicle=vehicle,
                start_date=start_date,
                end_date=end_date,
                status='pending',
            )
            messages.success(request, 'Booking created! Awaiting confirmation.')
            return redirect('dashboard')
    return redirect('vehicle_detail', pk=vehicle.pk)


def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Welcome to RentEasy!')
            return redirect('dashboard')
    else:
        form = UserRegistrationForm()
    return render(request, 'registration/register.html', {"form": form})


@login_required
def dashboard(request):
    my_bookings = Booking.objects.filter(user=request.user).select_related('vehicle')
    return render(request, 'rentals/dashboard.html', {"bookings": my_bookings})
