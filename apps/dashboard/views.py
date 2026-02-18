from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from django.views.decorators.http import require_http_methods
from datetime import datetime

from apps.reservations.models import Reservation
from apps.restaurants.models import Restaurant, Table


# ============================================================================
# DASHBOARD VIEWS
# ============================================================================

@login_required(login_url='auth:login')
@require_http_methods(["GET"])
def customer_dashboard(request):
    """Customer dashboard showing their reservations and profile."""
    # Get customer profile
    customer_profile = getattr(request.user, 'customer_profile', None)

    # Get upcoming and past reservations
    today = datetime.now().date()
    upcoming_reservations = Reservation.objects.filter(
        customer=request.user,
        reservation_date__gte=today,
        status__in=['pending', 'confirmed']
    ).order_by('reservation_date', 'reservation_time')[:5]

    past_reservations = Reservation.objects.filter(
        customer=request.user,
        reservation_date__lt=today
    ).order_by('-reservation_date')[:5]

    context = {
        'customer_profile': customer_profile,
        'upcoming_reservations': upcoming_reservations,
        'past_reservations': past_reservations,
    }
    return render(request, 'dashboards/customer_dashboard.html', context)


@login_required(login_url='auth:login')
@require_http_methods(["GET"])
def owner_dashboard(request):
    """Restaurant owner dashboard showing their restaurants and reservations."""
    # Get owner profile
    owner_profile = getattr(request.user, 'restaurant_owner_profile', None)

    # Get owner's restaurants
    restaurants = request.user.restaurants.all().order_by('-created_at')

    # Get recent reservations for all owner's restaurants
    recent_reservations = Reservation.objects.filter(
        table__restaurant__owner=request.user
    ).order_by('-reservation_date', '-reservation_time')[:10]

    # Get statistics
    total_restaurants = restaurants.count()
    total_tables = Table.objects.filter(restaurant__owner=request.user).count()
    total_reservations = Reservation.objects.filter(
        table__restaurant__owner=request.user
    ).count()
    pending_reservations = Reservation.objects.filter(
        table__restaurant__owner=request.user,
        status='pending'
    ).count()

    context = {
        'owner_profile': owner_profile,
        'restaurants': restaurants,
        'recent_reservations': recent_reservations,
        'total_restaurants': total_restaurants,
        'total_tables': total_tables,
        'total_reservations': total_reservations,
        'pending_reservations': pending_reservations,
    }
    return render(request, 'dashboards/owner_dashboard.html', context)


@login_required(login_url='auth:login')
@require_http_methods(["GET"])
def admin_dashboard(request):
    """Admin dashboard showing system statistics."""
    # Check if user is admin
    admin_profile = getattr(request.user, 'admin_profile', None)
    if not admin_profile:
        return HttpResponseForbidden('You do not have permission to access this page.')

    # Get system statistics
    total_users = request.user.__class__.objects.count()
    total_restaurants = Restaurant.objects.count()
    total_tables = Table.objects.count()
    total_reservations = Reservation.objects.count()
    pending_reservations = Reservation.objects.filter(status='pending').count()

    # Get recent activities
    recent_restaurants = Restaurant.objects.all().order_by('-created_at')[:5]
    recent_reservations = Reservation.objects.all().order_by('-created_at')[:5]

    context = {
        'total_users': total_users,
        'total_restaurants': total_restaurants,
        'total_tables': total_tables,
        'total_reservations': total_reservations,
        'pending_reservations': pending_reservations,
        'recent_restaurants': recent_restaurants,
        'recent_reservations': recent_reservations,
    }
    return render(request, 'dashboards/admin_dashboard.html', context)


@login_required(login_url='auth:login')
@require_http_methods(["GET"])
def owner_restaurants(request):
    """List owner's restaurants."""
    restaurants = request.user.restaurants.all().order_by('-created_at')
    context = {'restaurants': restaurants}
    return render(request, 'dashboards/owner_restaurants.html', context)


@login_required(login_url='auth:login')
@require_http_methods(["GET"])
def owner_menu(request):
    """Manage restaurant menu."""
    context = {}
    return render(request, 'dashboards/owner_menu.html', context)


@login_required(login_url='auth:login')
@require_http_methods(["GET"])
def owner_orders(request):
    """View restaurant orders."""
    context = {}
    return render(request, 'dashboards/owner_orders.html', context)


@login_required(login_url='auth:login')
@require_http_methods(["GET"])
def owner_tables(request):
    """Manage restaurant tables."""
    context = {}
    return render(request, 'dashboards/owner_tables.html', context)


@login_required(login_url='auth:login')
@require_http_methods(["GET"])
def owner_analytics(request):
    """View restaurant analytics."""
    context = {}
    return render(request, 'dashboards/owner_analytics.html', context)


@login_required(login_url='auth:login')
@require_http_methods(["GET"])
def owner_settings(request):
    """Restaurant settings."""
    context = {}
    return render(request, 'dashboards/owner_settings.html', context)


@login_required(login_url='auth:login')
@require_http_methods(["GET"])
def owner_subscription(request):
    """Manage subscription."""
    context = {}
    return render(request, 'dashboards/owner_subscription.html', context)


@login_required(login_url='auth:login')
@require_http_methods(["GET"])
def admin_users(request):
    """Manage all users."""
    admin_profile = getattr(request.user, 'admin_profile', None)
    if not admin_profile:
        return HttpResponseForbidden('You do not have permission to access this page.')

    context = {}
    return render(request, 'dashboards/admin_users.html', context)


@login_required(login_url='auth:login')
@require_http_methods(["GET"])
def admin_restaurants(request):
    """Manage all restaurants."""
    admin_profile = getattr(request.user, 'admin_profile', None)
    if not admin_profile:
        return HttpResponseForbidden('You do not have permission to access this page.')

    restaurants = Restaurant.objects.all().order_by('-created_at')
    context = {'restaurants': restaurants}
    return render(request, 'dashboards/admin_restaurants.html', context)


@login_required(login_url='auth:login')
@require_http_methods(["GET"])
def admin_orders(request):
    """View all orders."""
    admin_profile = getattr(request.user, 'admin_profile', None)
    if not admin_profile:
        return HttpResponseForbidden('You do not have permission to access this page.')

    context = {}
    return render(request, 'dashboards/admin_orders.html', context)


@login_required(login_url='auth:login')
@require_http_methods(["GET"])
def admin_analytics(request):
    """View system-wide analytics."""
    admin_profile = getattr(request.user, 'admin_profile', None)
    if not admin_profile:
        return HttpResponseForbidden('You do not have permission to access this page.')

    context = {}
    return render(request, 'dashboards/admin_analytics.html', context)


@login_required(login_url='auth:login')
@require_http_methods(["GET"])
def admin_subscriptions(request):
    """Manage all subscriptions."""
    admin_profile = getattr(request.user, 'admin_profile', None)
    if not admin_profile:
        return HttpResponseForbidden('You do not have permission to access this page.')

    context = {}
    return render(request, 'dashboards/admin_subscriptions.html', context)

