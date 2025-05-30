from django.urls import path
from . import views

app_name = 'resorts'

urlpatterns = [
    # Home and Authentication
    path('', views.home, name='home'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('register/', views.register, name='register'),

    # Resort Management
    path('resort/create/', views.resort_create, name='resort-create'),
    path('resort/<int:resort_id>/', views.resort_detail, name='resort-detail'),
    path('resort/<int:resort_id>/edit/', views.resort_edit, name='resort-edit'),
    path('resort/<int:resort_id>/delete/', views.resort_delete, name='resort-delete'),
    path('my-resorts/', views.my_resorts, name='my-resorts'),

    # Booking Management
    path('resort/<int:resort_id>/book/', views.create_booking, name='create-booking'),
    path('my-bookings/', views.my_bookings, name='my-bookings'),
    path('resort-bookings/', views.resort_bookings, name='resort-bookings'),
    path('booking/<int:booking_id>/respond/', views.booking_respond, name='booking-respond'),
    path('booking/<int:booking_id>/cancel/', views.cancel_booking, name='cancel-booking'),
]
