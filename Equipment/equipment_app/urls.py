from django.urls import path
from . import views
from .views import  PaymentSuccessView

urlpatterns = [
    # for user
    path('register/', views.register, name='register'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('profile/', views.profile, name='profile'),
    path('edit_profile/', views.edit_profile, name='edit_profile'),
    path('user_dashboard/',views.user_dashboard,name='user_dashboard'),
    path('list_equipment_user/',views.equipment_list_user,name='list_equipment_user'),
    path('equipment_search/', views.equipment_search, name='equipment_search'),
    path('book_equipment/<int:equipment_id>/', views.book_equipment, name='book_equipment'),
    path('cancel_booking/<int:booking_id>/', views.cancel_booking, name='cancel_booking'),
    path('payment/<int:booking_id>/', views.create_payment, name='payment'),
    # path('payment/<int:booking_id>/', CreatePaymentView.as_view(), name='create_payment'),
    path('payment_success/<int:booking_id>/', views.PaymentSuccessView, name='payment_success'),
    path('order_tracking/<int:booking_id>/', views.order_tracking, name='order_tracking'),
    path('equipment_location/', views.equipment_location, name='equipment_location'),
    path('add_location/<int:equipment_id>/', views.add_location, name='add_location'),
    path('leave_review/<int:equipment_id>/', views.leave_review, name='leave_review'),
    path('equipment/<int:equipment_id>/', views.equipment_details, name='equipment_details'),
    path('booked_equipment/',views.booked_equipment,name='booked_equipment'),


    path('',views.index,name="index"),

    # for admin
    path('admin_login/', views.admin_login, name='admin_login'),
    path('admin_logout/', views.admin_logout, name='admin_logout'),
    path('admin_dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('manage_users/', views.manage_users, name='manage_users'),
    path('approve_user/<int:user_id>/', views.approve_user, name='approve_user'),
    path('manage_equipment/', views.manage_equipment, name='manage_equipment'),
    path('approve_equipment/<int:equipment_id>/', views.approve_equipment, name='approve_equipment'),
    path('manage_booking/', views.admin_manage_bookings, name='manage_booking'),
    path('create_report/', views.create_report, name='create_report'),
    path('generate_report/', views.generate_report, name='generate_report'),
    path('download_report/<int:report_id>/', views.download_report, name='download_report'),
    path('manage_promotions/', views.manage_promotions, name='manage_promotions'),
    path('platform_settings_display/',views.platform_display_settings,name='platform_settings_display'),
    
    

    # for vendor
    path('vendor_register/', views.vendor_register, name='vendor_register'),
    path('vendor_login/', views.vendor_login, name='vendor_login'),
    path('vendor_logout/', views.vendor_logout, name='vendor_logout'),
    path('vendor_dashboard/', views.vendor_dashboard, name='vendor_dashboard'),
    path('vendor_profile/',views.vendor_profile,name='vendor_profile'),
    path('vendor_edit_profile/', views.edit_vendor_profile, name='edit_vendor_profile'),
    path('add_equipment/', views.add_equipment, name='add_equipment'),
    path('list_equipment/',views.equipment_list,name='list_equipment'),
    path('edit_equipment/<int:equipment_id>/', views.edit_equipment, name='edit_equipment'),
    path('delete_equipment/<int:equipment_id>/', views.delete_equipment, name='delete_equipment'),
    path('manage_bookings/', views.manage_bookings, name='manage_bookings'),
    path('approve_booking/<int:booking_id>/', views.approve_booking, name='approve_booking'),
    path('decline_booking/<int:booking_id>/', views.decline_booking, name='decline_booking'),
    path('manage_vendors/', views.manage_vendors, name='manage_vendors'),
    path('approve_vendor/<int:vendor_id>/', views.approve_vendor, name='approve_vendor'),
    path('disapprove_vendor/<int:vendor_id>/', views.disapprove_vendor, name='disapprove_vendor'),
    path('earnings/', views.earnings, name='earnings'),
    path('view_reviews/', views.view_reviews, name='view_reviews'),
    path('vendor_logout/', views.vendor_logout, name='vendor_logout'),

    # for Devliary 

    path('create_delivery_zone/', views.create_delivery_zone, name='create_delivery_zone'),
    path('manage_delivery_zone/', views.manage_delivery_zone, name='manage_delivery_zone'),
    path('update_delivery_zone/<int:zone_id>/', views.update_delivery_zone, name='update_delivery_zone'),
    path('create_restricted_area/', views.create_restricted_area, name='create_restricted_area'),
    path('manage_restricted_area/',views.manage_restricted_area,name='manage_restricted_area'),
    path('update_restricted_area/<int:area_id>/', views.update_restricted_area, name='update_restricted_area'),
    path('check_delivery_eligibility/', views.check_delivery_eligibility, name='check_delivery_eligibility'),
    path('delivery_status/<int:delivery_id>/', views.delivery_status, name='delivery_status'),
]



