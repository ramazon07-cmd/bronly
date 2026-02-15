from django.urls import path
from . import views

urlpatterns = [
    # Authentication URLs
    path('auth/signup/', views.signup_landing, name='signup_landing'),
    path('auth/signup/admin/', views.signup_admin, name='signup_admin'),
    path('auth/signup/restaurant-owner/', views.signup_restaurant_owner, name='signup_restaurant_owner'),
    path('auth/signup/customer/', views.signup_customer, name='signup_customer'),
    path('auth/login/', views.login_user, name='login_user'),
    path('auth/logout/', views.logout_user, name='logout_user'),
]
