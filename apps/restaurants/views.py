from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from django.core.paginator import Paginator
from django.views.decorators.http import require_http_methods
from datetime import datetime, timedelta

from .models import Restaurant, Table



# ============================================================================
# RESTAURANT PUBLIC VIEWS
# ============================================================================

@require_http_methods(["GET"])
def restaurant_list(request):
    """List all active restaurants."""
    restaurants = Restaurant.objects.filter(is_active=True).order_by('-created_at')

    # Pagination
    paginator = Paginator(restaurants, 10)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'restaurants': page_obj.object_list,
    }
    return render(request, 'restaurants/restaurant_list.html', context)


@require_http_methods(["GET"])
def restaurant_detail(request, restaurant_id):
    """View details of a single restaurant and its tables."""
    restaurant = get_object_or_404(Restaurant, id=restaurant_id, is_active=True)
    tables = restaurant.tables.filter(is_active=True).order_by('table_number')

    context = {
        'restaurant': restaurant,
        'tables': tables,
    }
    return render(request, 'restaurants/restaurant_detail.html', context)


# ============================================================================
# RESTAURANT OWNER VIEWS
# ============================================================================

@login_required(login_url='login_user')
@require_http_methods(["GET"])
def owner_restaurant_list(request):
    """List all restaurants owned by the logged-in user."""
    restaurants = request.user.restaurants.all().order_by('-created_at')

    context = {
        'restaurants': restaurants,
    }
    return render(request, 'restaurants/owner_restaurants.html', context)


@login_required(login_url='login_user')
@require_http_methods(["GET", "POST"])
def create_restaurant(request):
    """Create a new restaurant."""
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        description = request.POST.get('description', '').strip()
        cuisine_type = request.POST.get('cuisine_type', '').strip()
        phone = request.POST.get('phone', '').strip()
        email = request.POST.get('email', '').strip()
        website = request.POST.get('website', '').strip()
        address = request.POST.get('address', '').strip()
        city = request.POST.get('city', '').strip()
        postal_code = request.POST.get('postal_code', '').strip()
        opening_time = request.POST.get('opening_time', '').strip()
        closing_time = request.POST.get('closing_time', '').strip()

        # Basic validation
        errors = []
        if not name or not phone or not email or not address or not city or not cuisine_type:
            errors.append('Name, phone, email, address, city, and cuisine type are required.')
        if not opening_time or not closing_time:
            errors.append('Opening and closing times are required.')

        if not errors:
            # Handle file uploads
            logo = request.FILES.get('logo')
            cover_image = request.FILES.get('cover_image')

            restaurant = Restaurant.objects.create(
                owner=request.user,
                name=name,
                description=description,
                cuisine_type=cuisine_type,
                phone=phone,
                email=email,
                website=website,
                address=address,
                city=city,
                postal_code=postal_code,
                opening_time=opening_time,
                closing_time=closing_time,
                logo=logo if logo else None,
                cover_image=cover_image if cover_image else None,
            )
            return redirect('owner_restaurant_list')

        context = {'errors': errors}
        return render(request, 'restaurants/restaurant_form.html', context)

    context = {
        'cuisine_choices': Restaurant.CUISINE_CHOICES,
    }
    return render(request, 'restaurants/restaurant_form.html', context)


@login_required(login_url='login_user')
@require_http_methods(["GET", "POST"])
def update_restaurant(request, restaurant_id):
    """Update an existing restaurant."""
    restaurant = get_object_or_404(Restaurant, id=restaurant_id)

    # Verify ownership
    if restaurant.owner_id != request.user.id:
        return HttpResponseForbidden('You do not have permission to edit this restaurant.')

    if request.method == 'POST':
        restaurant.name = request.POST.get('name', '').strip() or restaurant.name
        restaurant.description = request.POST.get('description', '').strip()
        restaurant.cuisine_type = request.POST.get('cuisine_type', '').strip() or restaurant.cuisine_type
        restaurant.phone = request.POST.get('phone', '').strip() or restaurant.phone
        restaurant.email = request.POST.get('email', '').strip() or restaurant.email
        restaurant.website = request.POST.get('website', '').strip()
        restaurant.address = request.POST.get('address', '').strip() or restaurant.address
        restaurant.city = request.POST.get('city', '').strip() or restaurant.city
        restaurant.postal_code = request.POST.get('postal_code', '').strip() or restaurant.postal_code
        restaurant.opening_time = request.POST.get('opening_time', '').strip() or restaurant.opening_time
        restaurant.closing_time = request.POST.get('closing_time', '').strip() or restaurant.closing_time

        # Handle file uploads
        if 'logo' in request.FILES:
            restaurant.logo = request.FILES['logo']
        if 'cover_image' in request.FILES:
            restaurant.cover_image = request.FILES['cover_image']

        restaurant.save()
        return redirect('owner_restaurant_list')

    context = {
        'restaurant': restaurant,
        'cuisine_choices': Restaurant.CUISINE_CHOICES,
        'is_edit': True,
    }
    return render(request, 'restaurants/restaurant_form.html', context)


@login_required(login_url='login_user')
@require_http_methods(["GET", "POST"])
def delete_restaurant(request, restaurant_id):
    """Delete a restaurant."""
    restaurant = get_object_or_404(Restaurant, id=restaurant_id)

    # Verify ownership
    if restaurant.owner_id != request.user.id:
        return HttpResponseForbidden('You do not have permission to delete this restaurant.')

    if request.method == 'POST':
        restaurant.delete()
        return redirect('owner_restaurant_list')

    context = {
        'restaurant': restaurant,
        'confirm_delete': True,
    }
    return render(request, 'restaurants/confirm_delete.html', context)


# ============================================================================
# TABLE OWNER VIEWS
# ============================================================================

@login_required(login_url='login_user')
@require_http_methods(["GET", "POST"])
def create_table(request, restaurant_id):
    """Create a new table in a restaurant."""
    restaurant = get_object_or_404(Restaurant, id=restaurant_id)

    # Verify ownership
    if restaurant.owner_id != request.user.id:
        return HttpResponseForbidden('You do not have permission to add tables to this restaurant.')

    if request.method == 'POST':
        table_number = request.POST.get('table_number', '').strip()
        capacity = request.POST.get('capacity', '').strip()
        description = request.POST.get('description', '').strip()

        # Basic validation
        errors = []
        if not table_number or not capacity:
            errors.append('Table number and capacity are required.')
        if Table.objects.filter(restaurant=restaurant, table_number=table_number).exists():
            errors.append(f'Table {table_number} already exists in this restaurant.')

        if not errors:
            try:
                capacity_int = int(capacity)
                Table.objects.create(
                    restaurant=restaurant,
                    table_number=table_number,
                    capacity=capacity_int,
                    description=description,
                )
                return redirect('owner_restaurant_list')
            except ValueError:
                errors.append('Capacity must be a valid number.')

        context = {
            'restaurant': restaurant,
            'errors': errors,
        }
        return render(request, 'restaurants/table_form.html', context)

    context = {
        'restaurant': restaurant,
    }
    return render(request, 'restaurants/table_form.html', context)


@login_required(login_url='login_user')
@require_http_methods(["GET", "POST"])
def update_table(request, table_id):
    """Update a table."""
    table = get_object_or_404(Table, id=table_id)

    # Verify ownership
    if table.restaurant.owner_id != request.user.id:
        return HttpResponseForbidden('You do not have permission to edit this table.')

    if request.method == 'POST':
        table.table_number = request.POST.get('table_number', '').strip() or table.table_number
        capacity = request.POST.get('capacity', '').strip()
        table.description = request.POST.get('description', '').strip()

        errors = []
        if capacity:
            try:
                table.capacity = int(capacity)
            except ValueError:
                errors.append('Capacity must be a valid number.')

        if not errors:
            table.save()
            return redirect('owner_restaurant_list')

        context = {
            'table': table,
            'errors': errors,
            'is_edit': True,
        }
        return render(request, 'restaurants/table_form.html', context)

    context = {
        'table': table,
        'restaurant': table.restaurant,
        'is_edit': True,
    }
    return render(request, 'restaurants/table_form.html', context)


@login_required(login_url='login_user')
@require_http_methods(["GET", "POST"])
def delete_table(request, table_id):
    """Delete a table."""
    table = get_object_or_404(Table, id=table_id)

    # Verify ownership
    if table.restaurant.owner_id != request.user.id:
        return HttpResponseForbidden('You do not have permission to delete this table.')

    context = {
        'table': table,
        'confirm_delete': True,
    }
    return render(request, 'restaurants/confirm_delete.html', context)


# ============================================================================
# PUBLIC RESTAURANT MENU & RESERVATION ROUTES
# ============================================================================

@require_http_methods(["GET"])
def restaurant_menu(request, restaurant_slug):
    """View restaurant menu via QR code."""
    restaurant = get_object_or_404(Restaurant, slug=restaurant_slug, is_active=True)
    context = {'restaurant': restaurant}
    return render(request, 'restaurants/menu.html', context)


@require_http_methods(["GET", "POST"])
def reserve_table(request, restaurant_slug):
    """Make a reservation at a restaurant."""
    restaurant = get_object_or_404(Restaurant, slug=restaurant_slug, is_active=True)
    tables = restaurant.tables.filter(is_active=True).order_by('table_number')

    from apps.reservations.views import create_reservation
    # Delegate to reservations app
    context = {'restaurant': restaurant, 'tables': tables}
    return render(request, 'restaurants/reserve.html', context)


@login_required(login_url='auth:login')
@require_http_methods(["GET"])
def list_tables(request, restaurant_id):
    """List tables for a restaurant."""
    restaurant = get_object_or_404(Restaurant, id=restaurant_id)
    if restaurant.owner_id != request.user.id:
        return HttpResponseForbidden('You do not have permission to view this restaurant.')

    tables = restaurant.tables.all().order_by('table_number')
    context = {'restaurant': restaurant, 'tables': tables}
    return render(request, 'restaurants/list_tables.html', context)




