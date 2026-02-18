from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from django.core.paginator import Paginator
from django.views.decorators.http import require_http_methods
from django.db.models import Prefetch
from datetime import datetime

from .models import Reservation
from apps.restaurants.models import Table, Restaurant


# ============================================================================
# CUSTOMER RESERVATION VIEWS
# ============================================================================

@login_required(login_url='auth:login')
@require_http_methods(["GET"])
def customer_reservations(request):
    """List all reservations for the logged-in customer."""
    # Use select_related to prevent N+1 queries
    reservations = Reservation.objects.select_related(
        'customer',
        'table',
        'table__restaurant'
    ).filter(
        customer=request.user
    ).order_by('-reservation_date', '-reservation_time')

    # Pagination
    paginator = Paginator(reservations, 10)
    page_number = request.GET.get('page', 1)
    try:
        page_number = int(page_number)
    except ValueError:
        page_number = 1

    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'reservations': page_obj.object_list,
    }
    return render(request, 'reservations/customer_reservations.html', context)


@login_required(login_url='auth:login')
@require_http_methods(["GET"])
def reservation_detail(request, reservation_id):
    """View reservation details."""
    reservation = get_object_or_404(
        Reservation.objects.select_related('customer', 'table', 'table__restaurant'),
        id=reservation_id
    )

    # Verify permission: customer or restaurant owner
    is_customer = reservation.customer_id == request.user.id
    is_owner = reservation.table.restaurant.owner_id == request.user.id

    if not (is_customer or is_owner):
        return HttpResponseForbidden('You do not have permission to view this reservation.')

    context = {'reservation': reservation}
    return render(request, 'reservations/detail.html', context)


@login_required(login_url='auth:login')
@require_http_methods(["POST"])
def cancel_reservation(request, reservation_id):
    """Cancel a reservation (POST only)."""
    reservation = get_object_or_404(Reservation, id=reservation_id)

    # Verify permission: customer or restaurant owner
    is_customer = reservation.customer_id == request.user.id
    is_owner = reservation.table.restaurant.owner_id == request.user.id

    if not (is_customer or is_owner):
        return HttpResponseForbidden('You do not have permission to cancel this reservation.')

    # Only allow cancellation if not already cancelled or completed
    if reservation.status in ['cancelled', 'completed']:
        return HttpResponseForbidden('This reservation cannot be cancelled.')

    reservation.status = 'cancelled'
    reservation.save()

    # Redirect based on user role
    if is_customer:
        return redirect('reservations:customer_list')
    else:
        return redirect('reservations:restaurant_list', restaurant_id=reservation.table.restaurant.id)


# ============================================================================
# RESTAURANT OWNER VIEWS
# ============================================================================

@login_required(login_url='auth:login')
@require_http_methods(["GET"])
def restaurant_reservations(request, restaurant_id):
    """List all reservations for a restaurant (owner only)."""
    restaurant = get_object_or_404(Restaurant, id=restaurant_id)

    # Verify ownership
    if restaurant.owner_id != request.user.id:
        return HttpResponseForbidden('You do not have permission to view these reservations.')

    # Use select_related to prevent N+1 queries
    reservations = Reservation.objects.select_related(
        'customer',
        'table',
        'table__restaurant'
    ).filter(
        table__restaurant=restaurant
    ).order_by('-reservation_date', '-reservation_time')

    # Pagination
    paginator = Paginator(reservations, 10)
    page_number = request.GET.get('page', 1)
    try:
        page_number = int(page_number)
    except ValueError:
        page_number = 1

    page_obj = paginator.get_page(page_number)

    context = {
        'restaurant': restaurant,
        'page_obj': page_obj,
        'reservations': page_obj.object_list,
    }
    return render(request, 'reservations/restaurant_reservations.html', context)


@login_required(login_url='auth:login')
@require_http_methods(["POST"])
def confirm_reservation(request, reservation_id):
    """Confirm a pending reservation (owner only, POST only)."""
    reservation = get_object_or_404(Reservation, id=reservation_id)

    # Verify owner permission
    if reservation.table.restaurant.owner_id != request.user.id:
        return HttpResponseForbidden('You do not have permission to confirm this reservation.')

    # Only allow confirmation if pending
    if reservation.status != 'pending':
        return HttpResponseForbidden('This reservation cannot be confirmed.')

    reservation.status = 'confirmed'
    reservation.save()

    return redirect(
        'reservations:restaurant_list',
        restaurant_id=reservation.table.restaurant.id
    )
