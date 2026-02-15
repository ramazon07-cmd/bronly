from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.views.decorators.http import require_http_methods

from .models import User, Admin, RestaurantOwner, Customer


@require_http_methods(["GET"])
def signup_landing(request):
    """Show user role selection: Admin/RestaurantOwner/Customer."""
    if request.user.is_authenticated:
        return redirect('restaurant_list')
    return render(request, 'auth/signup_landing.html')


@require_http_methods(["GET", "POST"])
def signup_admin(request):
    """Admin registration form."""
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '').strip()
        password_confirm = request.POST.get('password_confirm', '').strip()
        first_name = request.POST.get('first_name', '').strip()
        last_name = request.POST.get('last_name', '').strip()
        phone = request.POST.get('phone', '').strip()
        title = request.POST.get('title', '').strip()

        errors = []
        if not username or not email or not password:
            errors.append('Username, email, and password are required.')
        if password != password_confirm:
            errors.append('Passwords do not match.')
        if User.objects.filter(username=username).exists():
            errors.append('Username already exists.')
        if User.objects.filter(email=email).exists():
            errors.append('Email already registered.')

        if not errors:
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name,
                phone=phone,
            )
            Admin.objects.create(user=user, title=title)
            return redirect('login_user')

        context = {'errors': errors}
        return render(request, 'auth/signup_admin.html', context)

    return render(request, 'auth/signup_admin.html')


@require_http_methods(["GET", "POST"])
def signup_restaurant_owner(request):
    """Restaurant owner registration form."""
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '').strip()
        password_confirm = request.POST.get('password_confirm', '').strip()
        first_name = request.POST.get('first_name', '').strip()
        last_name = request.POST.get('last_name', '').strip()
        phone = request.POST.get('phone', '').strip()
        business_license = request.POST.get('business_license', '').strip()

        errors = []
        if not username or not email or not password:
            errors.append('Username, email, and password are required.')
        if password != password_confirm:
            errors.append('Passwords do not match.')
        if User.objects.filter(username=username).exists():
            errors.append('Username already exists.')
        if User.objects.filter(email=email).exists():
            errors.append('Email already registered.')

        if not errors:
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name,
                phone=phone,
            )
            RestaurantOwner.objects.create(user=user, business_license=business_license)
            return redirect('login_user')

        context = {'errors': errors}
        return render(request, 'auth/signup_restaurant_owner.html', context)

    return render(request, 'auth/signup_restaurant_owner.html')


@require_http_methods(["GET", "POST"])
def signup_customer(request):
    """Customer registration form."""
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '').strip()
        password_confirm = request.POST.get('password_confirm', '').strip()
        first_name = request.POST.get('first_name', '').strip()
        last_name = request.POST.get('last_name', '').strip()
        phone = request.POST.get('phone', '').strip()
        dietary_preferences = request.POST.get('dietary_preferences', '').strip()

        errors = []
        if not username or not email or not password:
            errors.append('Username, email, and password are required.')
        if password != password_confirm:
            errors.append('Passwords do not match.')
        if User.objects.filter(username=username).exists():
            errors.append('Username already exists.')
        if User.objects.filter(email=email).exists():
            errors.append('Email already registered.')

        if not errors:
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name,
                phone=phone,
            )
            Customer.objects.create(user=user, dietary_preferences=dietary_preferences)
            return redirect('login_user')

        context = {'errors': errors}
        return render(request, 'auth/signup_customer.html', context)

    return render(request, 'auth/signup_customer.html')


@require_http_methods(["GET", "POST"])
def login_user(request):
    """Login for all user types."""
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '').strip()

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            # Determine role and redirect appropriately
            if hasattr(user, 'admin_profile'):
                return redirect('restaurant_list')  # Redirect to appropriate admin page
            elif hasattr(user, 'restaurant_owner_profile'):
                return redirect('owner_restaurant_list')
            elif hasattr(user, 'customer_profile'):
                return redirect('restaurant_list')  # Redirect to customer dashboard
            else:
                return redirect('restaurant_list')
        else:
            context = {'error': 'Invalid username or password.'}
            return render(request, 'auth/login.html', context)

    return render(request, 'auth/login.html')


@require_http_methods(["GET"])
def logout_user(request):
    """Logout for all user types."""
    logout(request)
    return redirect('restaurant_list')
