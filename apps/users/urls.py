"""
User Authentication URLs

URL Prefix: /auth/ (configured in core/urls.py)

Routes:
    /auth/login/                    → User login
    /auth/logout/                   → User logout
    /auth/register/                 → Role selection for signup
    /auth/register/admin/           → Admin signup
    /auth/register/owner/           → Restaurant owner signup
    /auth/register/customer/        → Customer signup

Template Usage:
    {% url 'auth:login' %}
    {% url 'auth:logout' %}
    {% url 'auth:register' %}
    {% url 'auth:register_admin' %}
    {% url 'auth:register_owner' %}
    {% url 'auth:register_customer' %}
"""

from django.urls import path
from . import views

app_name = "users"

urlpatterns = [
    # Login / Logout
    path("login/", views.login_user, name="login"),
    path("logout/", views.logout_user, name="logout"),

    # Signup - Role Selection
    path("register/", views.signup_landing, name="register"),

    # Signup - Role-Specific
    path("register/admin/", views.signup_admin, name="register_admin"),
    path("register/owner/", views.signup_restaurant_owner, name="register_owner"),
    path("register/customer/", views.signup_customer, name="register_customer"),
]
