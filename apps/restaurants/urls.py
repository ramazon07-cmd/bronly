from django.urls import path
from . import views

urlpatterns = [
    # Public restaurant views
    path('', views.restaurant_list, name='restaurant_list'),
    path('<int:restaurant_id>/', views.restaurant_detail, name='restaurant_detail'),

    # Authentication views
    path('auth/register/', views.register_owner, name='register_owner'),
    path('auth/login/', views.login_owner, name='login_owner'),
    path('auth/logout/', views.logout_owner, name='logout_owner'),

    # Owner restaurant management views
    path('owner/restaurants/', views.owner_restaurant_list, name='owner_restaurant_list'),
    path('owner/restaurants/create/', views.create_restaurant, name='create_restaurant'),
    path('owner/restaurants/<int:restaurant_id>/edit/', views.update_restaurant, name='update_restaurant'),
    path('owner/restaurants/<int:restaurant_id>/delete/', views.delete_restaurant, name='delete_restaurant'),

    # Owner table management views
    path('restaurants/<int:restaurant_id>/tables/create/', views.create_table, name='create_table'),
    path('tables/<int:table_id>/edit/', views.update_table, name='update_table'),
    path('tables/<int:table_id>/delete/', views.delete_table, name='delete_table'),
]
