from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from django.core.paginator import Paginator
from django.views.decorators.http import require_http_methods
from django.db.models import Q
from datetime import datetime, timedelta, time
from decimal import Decimal

from .models import Restaurant, Table
from .forms import RestaurantForm, TableForm


# ============================================================================
# RESTAURANT OWNER MANAGEMENT VIEWS
# ============================================================================

@login_required(login_url='auth:login')
@require_http_methods(["GET"])
def owner_restaurant_list(request):
    """List all restaurants owned by the logged-in user."""
    restaurants = request.user.restaurants.all().order_by('-created_at')

    context = {
        'restaurants': restaurants,
    }
    return render(request, 'dashboards/owner_restaurants.html', context)


@login_required(login_url='auth:login')
@require_http_methods(["GET", "POST"])
def create_restaurant(request):
    """Create a new restaurant (slug auto-generated from name)."""
    if request.method == 'POST':
        form = RestaurantForm(request.POST, request.FILES)
        if form.is_valid():
            restaurant = form.save(commit=False)
            restaurant.owner = request.user
            # Slug auto-generated in model.save()
            restaurant.save()
            return redirect('dashboard:owner_restaurants')
        else:
            context = {'form': form}
            return render(request, 'dashboards/restaurant_form.html', context)

    form = RestaurantForm()
    context = {'form': form}
    return render(request, 'dashboards/restaurant_form.html', context)


@login_required(login_url='auth:login')
@require_http_methods(["GET", "POST"])
def update_restaurant(request, restaurant_id):
    """Update an existing restaurant."""
    restaurant = get_object_or_404(Restaurant, id=restaurant_id)

    # Verify ownership
    if restaurant.owner_id != request.user.id:
        return HttpResponseForbidden('You do not have permission to edit this restaurant.')

    if request.method == 'POST':
        form = RestaurantForm(request.POST, request.FILES, instance=restaurant)
        if form.is_valid():
            form.save()
            return redirect('dashboard:owner_restaurants')
        else:
            context = {'form': form, 'restaurant': restaurant, 'is_edit': True}
            return render(request, 'dashboards/restaurant_form.html', context)

    form = RestaurantForm(instance=restaurant)
    context = {'form': form, 'restaurant': restaurant, 'is_edit': True}
    return render(request, 'dashboards/restaurant_form.html', context)


@login_required(login_url='auth:login')
@require_http_methods(["POST"])
def delete_restaurant(request, restaurant_id):
    """Delete a restaurant (POST only)."""
    restaurant = get_object_or_404(Restaurant, id=restaurant_id)

    # Verify ownership
    if restaurant.owner_id != request.user.id:
        return HttpResponseForbidden('You do not have permission to delete this restaurant.')

    restaurant.delete()
    return redirect('dashboard:owner_restaurants')


# ============================================================================
# TABLE MANAGEMENT VIEWS
# ============================================================================

@login_required(login_url='auth:login')
@require_http_methods(["GET", "POST"])
def create_table(request, restaurant_id):
    """Create a new table in a restaurant."""
    restaurant = get_object_or_404(Restaurant, id=restaurant_id)

    # Verify ownership
    if restaurant.owner_id != request.user.id:
        return HttpResponseForbidden('You do not have permission to add tables to this restaurant.')

    if request.method == 'POST':
        form = TableForm(request.POST)
        if form.is_valid():
            # Check for duplicate table number in this restaurant
            if Table.objects.filter(
                restaurant=restaurant,
                table_number=form.cleaned_data['table_number']
            ).exists():
                form.add_error('table_number', f"Table {form.cleaned_data['table_number']} already exists.")
                context = {'form': form, 'restaurant': restaurant}
                return render(request, 'dashboards/table_form.html', context)

            table = form.save(commit=False)
            table.restaurant = restaurant
            table.save()
            return redirect('dashboard:owner_restaurants')
        else:
            context = {'form': form, 'restaurant': restaurant}
            return render(request, 'dashboards/table_form.html', context)

    form = TableForm()
    context = {'form': form, 'restaurant': restaurant}
    return render(request, 'dashboards/table_form.html', context)


@login_required(login_url='auth:login')
@require_http_methods(["GET", "POST"])
def update_table(request, table_id):
    """Update a table."""
    table = get_object_or_404(Table, id=table_id)

    # Verify ownership
    if table.restaurant.owner_id != request.user.id:
        return HttpResponseForbidden('You do not have permission to edit this table.')

    if request.method == 'POST':
        form = TableForm(request.POST, instance=table)
        if form.is_valid():
            form.save()
            return redirect('dashboard:owner_restaurants')
        else:
            context = {'form': form, 'table': table, 'restaurant': table.restaurant, 'is_edit': True}
            return render(request, 'dashboards/table_form.html', context)

    form = TableForm(instance=table)
    context = {'form': form, 'table': table, 'restaurant': table.restaurant, 'is_edit': True}
    return render(request, 'dashboards/table_form.html', context)


@login_required(login_url='auth:login')
@require_http_methods(["POST"])
def delete_table(request, table_id):
    """Delete a table (POST only)."""
    table = get_object_or_404(Table, id=table_id)

    # Verify ownership
    if table.restaurant.owner_id != request.user.id:
        return HttpResponseForbidden('You do not have permission to delete this table.')

    restaurant_id = table.restaurant.id
    table.delete()
    return redirect('dashboard:owner_restaurants')


@login_required(login_url='auth:login')
@require_http_methods(["GET"])
def list_tables(request, restaurant_id):
    """List tables for a restaurant."""
    restaurant = get_object_or_404(Restaurant, id=restaurant_id)

    if restaurant.owner_id != request.user.id:
        return HttpResponseForbidden('You do not have permission to view this restaurant.')

    tables = restaurant.tables.all().order_by('table_number')
    context = {'restaurant': restaurant, 'tables': tables}
    return render(request, 'restaurants/restaurant_detail.html', context)


# ============================================================================
# PUBLIC RESTAURANT PAGES (Multi-Tenant, Slug-Based)
# These are used for customer-facing pages with slug routing
# ============================================================================

@require_http_methods(["GET"])
def restaurant_list(request):
    """List all active restaurants for public browsing."""
    restaurants = Restaurant.objects.filter(is_active=True).order_by('-created_at')

    context = {
        'restaurants': restaurants,
    }
    return render(request, 'restaurants/restaurant_list.html', context)


@require_http_methods(["GET"])
def restaurant_detail(request, restaurant_slug):
    """View public restaurant page with details and tables."""
    restaurant = get_object_or_404(Restaurant, slug=restaurant_slug, is_active=True)
    tables = restaurant.tables.filter(is_active=True).order_by('table_number')

    context = {
        'restaurant': restaurant,
        'tables': tables,
    }
    return render(request, 'restaurants/restaurant_detail.html', context)


@require_http_methods(["GET"])
def restaurant_menu(request, restaurant_slug):
    """View restaurant menu."""
    restaurant = get_object_or_404(Restaurant, slug=restaurant_slug, is_active=True)
    context = {'restaurant': restaurant}
    return render(request, 'restaurants/restaurant_detail.html', context)


@require_http_methods(["GET"])
def restaurant_about(request, restaurant_slug):
    """View restaurant about page."""
    restaurant = get_object_or_404(Restaurant, slug=restaurant_slug, is_active=True)
    context = {'restaurant': restaurant}
    return render(request, 'restaurants/restaurant_detail.html', context)


@require_http_methods(["GET"])
def restaurant_contact(request, restaurant_slug):
    """View restaurant contact information."""
    restaurant = get_object_or_404(Restaurant, slug=restaurant_slug, is_active=True)
    context = {'restaurant': restaurant}
    return render(request, 'restaurants/restaurant_detail.html', context)


@require_http_methods(["GET"])
def restaurant_gallery(request, restaurant_slug):
    """View restaurant gallery."""
    restaurant = get_object_or_404(Restaurant, slug=restaurant_slug, is_active=True)
    context = {'restaurant': restaurant}
    return render(request, 'restaurants/restaurant_detail.html', context)


@login_required(login_url='auth:login')
@require_http_methods(["GET", "POST"])
def create_public_reservation(request, restaurant_slug):
    """Create a public reservation (customer booking via slug)."""
    restaurant = get_object_or_404(Restaurant, slug=restaurant_slug, is_active=True)
    tables = restaurant.tables.filter(is_active=True).order_by('capacity')

    if request.method == 'POST':
        from apps.reservations.models import Reservation
        from .forms import PublicReservationForm

        form = PublicReservationForm(request.POST, restaurant=restaurant)
        if form.is_valid():
            # All validation handled by form (date, time, overlap, hours, etc.)
            reservation = form.save(commit=False)
            reservation.customer = request.user
            reservation.save()
            return redirect('reservations:detail', reservation_id=reservation.id)
        else:
            context = {
                'form': form,
                'restaurant': restaurant,
                'tables': tables,
            }
            return render(request, 'reservations/reservation_form.html', context)

    # GET request
    form = PublicReservationForm(restaurant=restaurant)
    context = {
        'form': form,
        'restaurant': restaurant,
        'tables': tables,
    }
    return render(request, 'reservations/reservation_form.html', context)
