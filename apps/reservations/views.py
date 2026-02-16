from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from django.core.paginator import Paginator
from django.views.decorators.http import require_http_methods
from datetime import datetime

from .models import Reservation
from apps.restaurants.models import Table


# ============================================================================
# RESERVATION VIEWS
# ============================================================================

@login_required(login_url='login_user')
@require_http_methods(["GET", "POST"])
def create_reservation(request, table_id):
    """Create a new reservation for a table."""
    table = get_object_or_404(Table, id=table_id)
    restaurant = table.restaurant

    if request.method == 'POST':
        reservation_date = request.POST.get('reservation_date', '').strip()
        reservation_time = request.POST.get('reservation_time', '').strip()
        guest_count = request.POST.get('guest_count', '').strip()
        special_requests = request.POST.get('special_requests', '').strip()

        errors = []
        if not reservation_date or not reservation_time or not guest_count:
            errors.append('Reservation date, time, and guest count are required.')

        try:
            guest_count_int = int(guest_count)
            if guest_count_int <= 0 or guest_count_int > table.capacity:
                errors.append(f'Guest count must be between 1 and {table.capacity}.')
        except ValueError:
            errors.append('Guest count must be a valid number.')

        if not errors:
            reservation = Reservation.objects.create(
                customer=request.user,
                table=table,
                reservation_date=reservation_date,
                reservation_time=reservation_time,
                guest_count=int(guest_count),
                special_requests=special_requests,
            )
            return redirect('customer_reservations')

        context = {
            'table': table,
            'restaurant': restaurant,
            'errors': errors,
        }
        return render(request, 'reservations/reservation_form.html', context)

    context = {
        'table': table,
        'restaurant': restaurant,
        'min_date': datetime.now().date(),
    }
    return render(request, 'reservations/reservation_form.html', context)


@login_required(login_url='login_user')
@require_http_methods(["GET"])
def customer_reservations(request):
    """List all reservations for the logged-in customer."""
    reservations = Reservation.objects.filter(customer=request.user).order_by('-reservation_date', '-reservation_time')

    # Pagination
    paginator = Paginator(reservations, 10)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'reservations': page_obj.object_list,
    }
    return render(request, 'reservations/customer_reservations.html', context)


@login_required(login_url='login_user')
@require_http_methods(["GET"])
def restaurant_reservations(request, restaurant_id):
    """List all reservations for a restaurant (owner only)."""
    from apps.restaurants.models import Restaurant
    restaurant = get_object_or_404(Restaurant, id=restaurant_id)

    # Verify ownership
    if restaurant.owner_id != request.user.id:
        return HttpResponseForbidden('You do not have permission to view these reservations.')

    reservations = Reservation.objects.filter(table__restaurant=restaurant).order_by('-reservation_date', '-reservation_time')

    # Pagination
    paginator = Paginator(reservations, 10)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)

    context = {
        'restaurant': restaurant,
        'page_obj': page_obj,
        'reservations': page_obj.object_list,
    }
    return render(request, 'reservations/restaurant_reservations.html', context)


@login_required(login_url='login_user')
@require_http_methods(["GET", "POST"])
def cancel_reservation(request, reservation_id):
    """Cancel a reservation."""
    reservation = get_object_or_404(Reservation, id=reservation_id)

    # Verify customer or owner permission
    is_customer = reservation.customer_id == request.user.id
    is_owner = reservation.table.restaurant.owner_id == request.user.id

    if not (is_customer or is_owner):
        return HttpResponseForbidden('You do not have permission to cancel this reservation.')

    if request.method == 'POST':
        reservation.status = 'cancelled'
        reservation.save()
        if is_customer:
            return redirect('customer_reservations')
        else:
            return redirect('restaurant_reservations', restaurant_id=reservation.table.restaurant.id)

    context = {
        'reservation': reservation,
    }
    return render(request, 'reservations/cancel_reservation.html', context)


@login_required(login_url='auth:login')
@require_http_methods(["GET"])
def reservation_detail(request, reservation_id):
    """View reservation details."""
    reservation = get_object_or_404(Reservation, id=reservation_id)

    # Verify permission
    is_customer = reservation.customer_id == request.user.id
    is_owner = reservation.table.restaurant.owner_id == request.user.id

    if not (is_customer or is_owner):
        return HttpResponseForbidden('You do not have permission to view this reservation.')

    context = {'reservation': reservation}
    return render(request, 'reservations/detail.html', context)


@login_required(login_url='auth:login')
@require_http_methods(["GET", "POST"])
def confirm_reservation(request, reservation_id):
    """Confirm a pending reservation (owner only)."""
    reservation = get_object_or_404(Reservation, id=reservation_id)

    # Verify owner permission
    if reservation.table.restaurant.owner_id != request.user.id:
        return HttpResponseForbidden('You do not have permission to confirm this reservation.')

    if request.method == 'POST':
        reservation.status = 'confirmed'
        reservation.save()
        return redirect('reservations:restaurant_list', restaurant_id=reservation.table.restaurant.id)

    context = {'reservation': reservation}
    return render(request, 'reservations/confirm.html', context)

