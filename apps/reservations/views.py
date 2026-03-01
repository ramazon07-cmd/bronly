from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden, JsonResponse
from django.core.paginator import Paginator
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Prefetch
from django.db import transaction
from datetime import datetime
import json

from .models import Reservation
from apps.restaurants.models import Table, Restaurant
from .forms import AvailabilityCheckForm, ReservationForm


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


@login_required(login_url='auth:login')
@require_http_methods(["GET"])
def reservation_deposit(request, reservation_id):
    """Display reservation details and deposit payment page."""
    reservation = get_object_or_404(
        Reservation.objects.select_related('customer', 'table', 'table__restaurant'),
        id=reservation_id
    )
    
    # Verify permission: customer who made reservation
    if reservation.customer_id != request.user.id:
        return HttpResponseForbidden('You do not have permission to view this reservation.')
    
    # Calculate deposit amount if not set (for demo purposes, using a simple calculation)
    if not reservation.deposit_amount:
        # Set deposit to $20 per person as default
        reservation.deposit_amount = reservation.guest_count * 20
        reservation.save()
    
    context = {
        'reservation': reservation,
        'deposit_amount': reservation.deposit_amount,
    }
    return render(request, 'reservations/deposit.html', context)


@csrf_exempt
@login_required(login_url='auth:login')
@require_http_methods(["POST"])
def check_availability_ajax(request):
    """AJAX endpoint to check table availability in real-time."""
    try:
        # Parse JSON data from request
        data = json.loads(request.body)
        form_data = {
            'table_id': data.get('table_id'),
            'reservation_date': data.get('date'),
            'reservation_time': data.get('time')
        }
        
        form = AvailabilityCheckForm(data=form_data)
        if form.is_valid():
            # If validation passes, the table is available
            return JsonResponse({
                'success': True,
                'available': True,
                'message': 'Table is available for the selected time.'
            })
        else:
            # Return validation errors
            return JsonResponse({
                'success': False,
                'available': False,
                'errors': form.errors
            })
    
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': 'Invalid JSON data'
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@csrf_exempt
@login_required(login_url='auth:login')
@require_http_methods(["POST"])
def create_reservation_ajax(request):
    """AJAX endpoint to create a reservation."""
    try:
        # Parse JSON data from request
        data = json.loads(request.body)
        
        # Prepare form data
        form_data = {
            'table': data.get('table_id'),
            'reservation_date': data.get('date'),
            'reservation_time': data.get('time'),
            'guest_count': data.get('guest_count', 1),
            'special_requests': data.get('special_requests', '')
        }
        
        # Create form with restaurant context if available
        restaurant_id = data.get('restaurant_id')
        restaurant = None
        if restaurant_id:
            try:
                from apps.restaurants.models import Restaurant
                restaurant = Restaurant.objects.get(id=restaurant_id)
            except Restaurant.DoesNotExist:
                pass
        
        form = ReservationForm(data=form_data, restaurant=restaurant)
        if form.is_valid():
            with transaction.atomic():
                reservation = form.save(commit=False)
                reservation.customer = request.user
                reservation.save()
                
                return JsonResponse({
                    'success': True,
                    'reservation_id': reservation.id,
                    'message': 'Reservation created successfully.',
                    'redirect_url': f'/reservations/{reservation.id}/deposit/'
                })
        else:
            # Return validation errors
            return JsonResponse({
                'success': False,
                'errors': form.errors
            })
    
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': 'Invalid JSON data'
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)
