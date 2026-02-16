from django.urls import path
from . import views


urlpatterns = [
    # Dashboard views
    path('dashboard/customer/', views.customer_dashboard, name='customer_dashboard'),
    path('dashboard/owner/', views.owner_dashboard, name='owner_dashboard'),
    path('dashboard/admin/', views.admin_dashboard, name='admin_dashboard'),
]
