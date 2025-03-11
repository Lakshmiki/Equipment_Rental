from django.shortcuts import render,redirect,get_object_or_404
from django.contrib.auth.decorators import login_required,user_passes_test
from .models import *
from .forms import *
from django.contrib.auth import login, authenticate, logout
from datetime import date, timedelta
# from django.contrib import messages
from django.contrib import messages
from django.http import HttpResponse
import csv
import stripe
from django.conf import settings
import razorpay
from django.views.decorators.csrf import csrf_exempt
from django.views import View
from django.core.paginator import Paginator
client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))


# stripe.api_key = settings.STRIPE_SECRET_KEY



# Create your views here.
def is_admin(user):
    return user.is_staff

def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save()
            # Create UserProfile
            UserProfile.objects.create(
                user=user,
                phone_number=form.cleaned_data['phone_number'],
                address=form.cleaned_data['address'],
                id_proof=form.cleaned_data['id_proof']
            )
            login(request, user)
            return redirect('login')
    else:
        form = UserRegistrationForm()
    return render(request, 'user_register.html', {'form': form})

# def user_login(request):
#     if request.method == 'POST':
#         form = UserLoginForm(request, data=request.POST)
#         if form.is_valid():
#             username = form.cleaned_data.get('username')
#             password = form.cleaned_data.get('password')
#             user = authenticate(username=username, password=password)
#             if user is not None:
#                 login(request, user)
#                 return redirect('user_dashboard')
#     else:
#         form = UserLoginForm()
#     return render(request, 'user_login.html', {'form': form})


# # User Logout
# @login_required
# def user_logout(request):
#     logout(request)
#     return redirect('login')
# def user_login(request):
#     if request.method == 'POST':
#         form = UserLoginForm(request, data=request.POST)
#         if form.is_valid():
#             username = form.cleaned_data.get('username')
#             password = form.cleaned_data.get('password')
#             user = authenticate(username=username, password=password)
#             if user is not None:
#                 login(request, user)
#                 messages.success(request, "Login successful! Welcome back.")
#                 return redirect('user_dashboard')
#             else:
#                 messages.error(request, "Invalid username or password. Please try again.")
#         else:
#             messages.warning(request, "There was an error in the form. Please check your input.")
#     else:
#         form = UserLoginForm()
    
#     return render(request, 'user_login.html', {'form': form})
def user_login(request):
    if request.method == 'POST':
        form = UserLoginForm(request, data=request.POST)
        if form.is_valid():
            email = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            try:
                user = User.objects.get(email=email)
                username = user.username
                authenticated_user = authenticate(username=username, password=password)
                if authenticated_user is not None:
                    login(request, authenticated_user)
                    messages.success(request, "Login successful! Welcome back.")
                    return redirect('user_dashboard')
                else:
                    messages.error(request, "Invalid email or password. Please try again.")
            except User.DoesNotExist:
                messages.error(request, "Invalid email or password. Please try again.")
        else:
            messages.warning(request, "There was an error in the form. Please check your input.")
    else:
        form = UserLoginForm()
    
    return render(request, 'user_login.html', {'form': form})


@login_required
def user_logout(request):
    logout(request)
    messages.success(request, "You have been logged out successfully.")
    return redirect('login')

@login_required
def user_dashboard(request):
    # Get or create the UserProfile instance for the logged-in user
    # user_profile, created = UserProfile.objects.get_or_create(user=request.user)
    
    # # Fetch bookings for the logged-in user's profile
    # bookings = Booking.objects.filter(user=user_profile).select_related('equipment')
    
    # # Pass the bookings to the template
    # context = {
    #     'bookings': bookings
    # }
    return render(request, 'user_dashboard.html')
@login_required
def booked_equipment(request):
    # Get or create the UserProfile instance for the logged-in user
    user_profile, created = UserProfile.objects.get_or_create(user=request.user)
    
    # Fetch bookings for the logged-in user's profile
    bookings = Booking.objects.filter(user=user_profile).select_related('equipment')
    
    # Pass the bookings to the template
    context = {
        'bookings': bookings
    }
    return render(request, 'booked_equipment.html', context)


@login_required
def profile(request):
    user_profile = UserProfile.objects.get(user=request.user)
    return render(request, 'user_profile.html', {'profile': user_profile})

@login_required
def edit_profile(request):
    user_profile = UserProfile.objects.get(user=request.user)
    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=user_profile)
        if form.is_valid():
            form.save()
            return redirect('profile')
    else:
        form = UserProfileForm(instance=user_profile)
    return render(request, 'user_edit_profile.html', {'form': form})

def equipment_list_user(request):
   
    equipments = Equipment.objects.filter(is_approved=True)  
    return render(request, 'user_equipment_list.html', {'equipments': equipments})

def equipment_search(request):
    query = request.GET.get('query', '')
    equipment_list = Equipment.objects.filter(name__icontains=query, is_available=True)
    return render(request, 'user_equipment_list.html', {'equipment_list': equipment_list})


@login_required
def book_equipment(request, equipment_id):
    equipment = get_object_or_404(Equipment, id=equipment_id)
    if request.method == 'POST':
        form = BookingForm(request.POST)
        if form.is_valid():
            booking = form.save(commit=False)
            booking.equipment = equipment
            booking.user = request.user.userprofile
            booking.total_cost = calculate_total_cost(equipment, booking.start_date, booking.end_date)
            booking.payment_status = 'pending'
            booking.booking_status = 'pending'
            booking.save()
            return redirect('payment', booking_id=booking.id)
    else:
        form = BookingForm()
    return render(request, 'user_book_equipment.html', {'form': form, 'equipment': equipment})
def calculate_total_cost(equipment, start_date, end_date):
    rental_days = (end_date - start_date).days
    if rental_days >= 7:
        return equipment.price_per_week * (rental_days // 7)
    elif rental_days >= 1:
        return equipment.price_per_day * rental_days
    else:
        return equipment.price_per_hour
    
# @login_required
# def payment(request, booking_id):
#     booking = get_object_or_404(Booking, id=booking_id, user=request.user.userprofile)

#     if request.method == 'POST':
#         try:
#             # Ensure amount is an integer (cents)
#             amount = int(booking.total_cost * 100)

#             # Create a Stripe PaymentIntent
#             intent = stripe.PaymentIntent.create(
#                 amount=amount,
#                 currency='usd',
#                 metadata={'booking_id': booking.id},
#             )

#             return render(request, 'user_payment.html', {
#                 'booking': booking,
#                 'client_secret': intent.client_secret,
#                 'stripe_public_key': settings.STRIPE_PUBLIC_KEY,
#             })
#         except stripe.error.StripeError as e:
#             return render(request, 'user_payment.html', {
#                 'booking': booking,
#                 'error': str(e),
#             })

#     return render(request, 'user_payment.html', {'booking': booking})




# stripe.api_key = settings.STRIPE_SECRET_KEY

# @login_required
# def payment(request, booking_id):
#     booking = get_object_or_404(Booking, id=booking_id, user=request.user.userprofile)
    
#     stripe.api_key = settings.STRIPE_SECRET_KEY  # Ensure you set this in settings.py
    
#     # Create a PaymentIntent with the required description
#     intent = stripe.PaymentIntent.create(
#         amount=int(booking.total_cost * 100),  # Convert to cents
#         currency='usd',
#         description=f"Payment for {booking.equipment.name} (Booking ID: {booking.id})",
#         metadata={'booking_id': booking.id},
#     )
    
#     return render(request, 'user_payment.html', {
#         'booking': booking,
#         'stripe_public_key': settings.STRIPE_PUBLIC_KEY,
#         'client_secret': intent.client_secret,
#     })
# @login_required
# def payment_Demo(request):
#     if request.method == "POST":
#         name = request.POST.get('name')
#         amount = 50000

#         client = razorpay.Client(
#             auth=("rzp_test_LfpOSQiMWqsXgX", "5GlIvFEsgZDJckuGXPVeS1AA"))

#         payment = client.order.create({'amount': amount, 'currency': 'INR',
#                                        'payment_capture': '1'})
#     return render(request, 'user_payment.html')
# @csrf_exempt
# def payment_success(request):
#     return render(request, "success.html")

def create_payment(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id)
    
    # Convert total cost to paise (Razorpay requires amount in the smallest currency unit)
    amount = int(booking.total_cost * 100)  # INR to paise
    currency = "INR"

    # Create a Razorpay Order
    payment_order = client.order.create({
        'amount': amount,
        'currency': currency,
        'payment_capture': '1'  # Auto-capture payment
    })

    # Save the Razorpay order ID in the booking for future reference
    booking.razorpay_order_id = payment_order['id']
    booking.save()

    # Prepare context for the payment template
    context = {
        'booking': booking,
        'razorpay_key_id': settings.RAZORPAY_KEY_ID,
        'order_id': payment_order['id'],
        'amount': amount,
        'currency': currency,
    }

    return render(request, 'user_payment.html', context)

# class PaymentSuccessView(View):
#     def get(self, request, booking_id):
#         booking = get_object_or_404(Booking, id=booking_id)
#         booking.payment_status = 'full'
#         booking.booking_status = 'approved'
#         booking.save()
        

#         context = {
#             'booking': booking,
#         }
#         return render(request, 'payment_success.html', context)
# @login_required
# def PaymentSuccessView(request, booking_id):
#     booking = get_object_or_404(Booking, id=booking_id)
#     # Update payment and booking status
#     booking.payment_status = 'full'
#     booking.booking_status = 'approved'
#     booking.save()

#     # Redirect to order tracking with the booking_id
#     return redirect('order_tracking', booking_id=booking.id)
@login_required
def PaymentSuccessView(request, booking_id):
    # Fetch the booking
    booking = get_object_or_404(Booking, id=booking_id)

    # Update payment and booking status
    booking.payment_status = 'full'
    booking.booking_status = 'approved'
    booking.save()

    # Fetch the vendor profile associated with the equipment
    vendor_profile = booking.equipment.vendor

    # Create a transaction record for the vendor
    Transaction.objects.create(
        vendor=vendor_profile,
        booking=booking,
        amount=booking.total_cost,
        status='completed'  # Assuming payment is successful
    )
    return redirect('order_tracking', booking_id=booking.id)


@login_required
def order_tracking(request, booking_id):
    # Fetch the booking for the logged-in user
    booking = get_object_or_404(Booking, id=booking_id, user=request.user.userprofile)
    
    # Pass the booking details to the template
    context = {
        'booking': booking
    }
    return render(request, 'user_order_tracking.html', context)
@login_required
def leave_review(request, equipment_id):
    equipment = get_object_or_404(Equipment, id=equipment_id)
    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.equipment = equipment
            review.user = request.user.userprofile
            review.save()
            return redirect('equipment_details', equipment_id=equipment.id)
    else:
        form = ReviewForm()
    return render(request, 'user_leave_review.html', {'form': form, 'equipment': equipment})

def equipment_details(request, equipment_id):
    equipment = get_object_or_404(Equipment, id=equipment_id)
    reviews = Review.objects.filter(equipment=equipment).order_by('-created_at')
    return render(request, 'user_equipment_details.html', {'equipment': equipment, 'reviews': reviews})

def index(request):
    return render(request,'index.html')

def admin_dashboard(request):
    return render(request,'admin_dashboard.html')
def admin_login(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None and user.is_staff:  # Check if the user is an admin
                login(request, user)
                return redirect('admin_dashboard')
            else:
                form.add_error(None, "You do not have admin privileges.")
    else:
        form = AuthenticationForm()
    return render(request, 'admin_login.html', {'form': form})

@login_required
@user_passes_test(is_admin)
def admin_logout(request):
    logout(request)
    return redirect('admin_login')

# Admin Dashboard
@login_required
@user_passes_test(is_admin)
def admin_dashboard(request):
    return render(request, 'admin_dashboard.html')


@login_required
@user_passes_test(is_admin)
def manage_users(request):
    users = UserProfile.objects.all()
    return render(request, 'admin_manage_users.html', {'users': users})

@login_required
@user_passes_test(is_admin)
def approve_user(request, user_id):
    user = get_object_or_404(UserProfile, id=user_id)
    user.is_verified = True
    user.save()
    return redirect('manage_users')

@login_required
@user_passes_test(is_admin)
def manage_vendors(request):
    # Fetch all vendors
    vendors = VendorProfile.objects.all()
    return render(request, 'admin_manage_vendors.html', {'vendors': vendors})
@login_required
@user_passes_test(is_admin)
def approve_vendor(request, vendor_id):
    # Fetch the vendor profile
    vendor = get_object_or_404(VendorProfile, id=vendor_id)

    # Approve the vendor
    vendor.is_approved = True
    vendor.save()

    # Redirect back to the manage vendors page
    return redirect('manage_vendors')

@login_required
@user_passes_test(is_admin)
def disapprove_vendor(request, vendor_id):
    # Fetch the vendor profile
    vendor = get_object_or_404(VendorProfile, id=vendor_id)

    # Disapprove the vendor
    vendor.is_approved = False
    vendor.save()

    # Redirect back to the manage vendors page
    return redirect('manage_vendors')


@login_required
@user_passes_test(is_admin)
def approve_equipment(request, equipment_id):
    equipment = get_object_or_404(Equipment, id=equipment_id)
    equipment.is_approved = True
    equipment.save()
    return redirect('manage_equipment')

@login_required
@user_passes_test(is_admin)
def manage_equipment(request):
    equipment_list = Equipment.objects.filter(is_approved=False)
    if not equipment_list.exists():
        messages.info(request, "No unapproved equipment found.")
    return render(request, 'admin_manage_equipment.html', {'equipment_list': equipment_list})


# @login_required
# @user_passes_test(is_admin)
# def admin_manage_bookings(request):
#     bookings = Booking.objects.all()

#     if request.method == "POST":
#         booking_id = request.POST.get("booking_id")
#         new_status = request.POST.get("booking_status")

#         booking = Booking.objects.get(id=booking_id)
#         booking.booking_status = new_status
#         booking.save()

#         return redirect("manage_booking")  # Refresh the page

#     return render(request, "admin_manage_bookings.html", {"bookings": bookings})
@login_required
@user_passes_test(is_admin)
def admin_manage_bookings(request):
    bookings_list = Booking.objects.all().order_by('-created_at')  # Order by latest bookings
    paginator = Paginator(bookings_list, 5)  # Show 5 bookings per page

    page_number = request.GET.get('page')
    bookings = paginator.get_page(page_number)  # Get the requested page

    if request.method == "POST":
        booking_id = request.POST.get("booking_id")
        new_status = request.POST.get("booking_status")

        booking = Booking.objects.get(id=booking_id)
        booking.booking_status = new_status
        booking.save()

        return redirect("manage_booking")  # Refresh the page

    return render(request, "admin_manage_bookings.html", {"bookings": bookings})

@login_required
@user_passes_test(is_admin)
def create_report(request):
    if request.method == 'POST':
        form = ReportForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('generate_report')
    else:
        form = ReportForm()
    return render(request, 'admin_create_report.html', {'form': form})

@login_required
@user_passes_test(is_admin)
def generate_report(request):
    reports = Report.objects.all()
    return render(request, 'admin_generate_report.html', {'reports': reports})

@login_required
@user_passes_test(is_admin)
def download_report(request, report_id):
    report = Report.objects.get(id=report_id)
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="{report.report_type}.csv"'

    writer = csv.writer(response)
    writer.writerow(['Report Type', 'Generated At', 'Data'])
    writer.writerow([report.report_type, report.generated_at, report.data])

    return response

# @login_required
# @user_passes_test(is_admin)
# def platform_settings(request):
#     settings = PlatformSettings.objects.first()
#     if request.method == 'POST':
#         form = PlatformSettingsForm(request.POST, instance=settings)
#         if form.is_valid():
#             form.save()
#             return redirect('platform_settings_display')
#     else:
#         form = PlatformSettingsForm(instance=settings)
#     return render(request, 'admin_platform_settings.html', {'form': form})
@login_required
@user_passes_test(is_admin)
def platform_settings(request):
    # Fetch the first PlatformSettings object or create a new one if it doesn't exist
    settings, created = PlatformSettings.objects.get_or_create()

    if request.method == 'POST':
        form = PlatformSettingsForm(request.POST, instance=settings)
        if form.is_valid():
            form.save()
            return redirect('platform_settings_display')  # Redirect to the same page to display updated data
    else:
        form = PlatformSettingsForm(instance=settings)

    return render(request, 'admin_platform_settings.html', {'form': form})


@login_required
@user_passes_test(is_admin)
def platform_display_settings(request):
    # Fetch the platform settings (assuming only one instance exists)
    settings = PlatformSettings.objects.first()
    return render(request, 'admin_platform_display_settings.html', {'settings': settings})



def vendor_register(request):
    if request.method == 'POST':
        form = VendorRegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save()
            # Create VendorProfile
            VendorProfile.objects.create(
                user=user,
                company_name=form.cleaned_data['company_name'],
                description=form.cleaned_data['description'],
                phone_number=form.cleaned_data['phone_number'],
                business_license=form.cleaned_data['business_license']
            )
            login(request, user)
            return redirect('vendor_login')
    else:
        form = VendorRegistrationForm()
    return render(request, 'vendor_register.html', {'form': form})

# def vendor_login(request):
#     if request.method == 'POST':
#         form = VendorLoginForm(request.POST)
#         if form.is_valid():
#             username = form.cleaned_data.get('username')
#             password = form.cleaned_data.get('password')
#             user = authenticate(username=username, password=password)
#             if user is not None:
#                 login(request, user)
#                 return redirect('vendor_dashboard')
#     else:
#         form = VendorLoginForm()
#     return render(request, 'vendor_login.html', {'form': form})
def vendor_login(request):
    if request.method == 'POST':
        form = VendorLoginForm(request, data=request.POST)
        if form.is_valid():
            email = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            try:
                user = User.objects.get(email=email)
                username = user.username
                authenticated_user = authenticate(username=username, password=password)
                if authenticated_user is not None:
                    login(request, authenticated_user)
                    messages.success(request, "Login successful! Welcome back.")
                    return redirect('vendor_dashboard')
                else:
                    messages.error(request, "Invalid email or password. Please try again.")
            except User.DoesNotExist:
                messages.error(request, "Invalid email or password. Please try again.")
        else:
            messages.warning(request, "There was an error in the form. Please check your input.")
    else:
        form = UserLoginForm()
    
    return render(request, 'vendor_login.html', {'form': form})



@login_required
def vendor_logout(request):
    logout(request)
    return redirect('home')

# Vendor Dashboard
@login_required
def vendor_profile(request):
    vendor_profile = VendorProfile.objects.get(user=request.user)
    return render(request, 'vendor_profile_view.html', {'profile': vendor_profile})

@login_required
def vendor_dashboard(request):
    return render(request,'vendor_dashboard.html')

# Edit Vendor Profile
@login_required
def edit_vendor_profile(request):
    vendor_profile = VendorProfile.objects.get(user=request.user)
    if request.method == 'POST':
        form = VendorProfileForm(request.POST, instance=vendor_profile)
        if form.is_valid():
            form.save()
            return redirect('vendor_dashboard')
    else:
        form = VendorProfileForm(instance=vendor_profile)
    return render(request, 'vendor_edit_profile.html', {'form': form})

@login_required
def add_equipment(request):
    if request.method == 'POST':
        form = EquipmentForm(request.POST, request.FILES)
        if form.is_valid():
            equipment = form.save(commit=False)
            equipment.vendor = request.user.vendorprofile
            equipment.save()
            return redirect('vendor_dashboard')
    else:
        form = EquipmentForm()
    return render(request, 'vendor_add_equipment.html', {'form': form})

@login_required
def equipment_list(request):
    equipments = Equipment.objects.filter(vendor=request.user.vendorprofile)
    return render(request, 'vendor_equipment_list.html', {'equipments': equipments})

@login_required
def edit_equipment(request, equipment_id):
    equipment = get_object_or_404(Equipment, id=equipment_id, vendor=request.user.vendorprofile)
    if request.method == 'POST':
        form = EquipmentForm(request.POST, request.FILES, instance=equipment)
        if form.is_valid():
            form.save()
            return redirect('vendor_dashboard')
    else:
        form = EquipmentForm(instance=equipment)
    return render(request, 'vendor_edit_equipment.html', {'form': form})

@login_required
def delete_equipment(request, equipment_id):
    
    equipment = get_object_or_404(Equipment, id=equipment_id, vendor=request.user.vendorprofile)

    if request.method == 'POST':
        
        equipment.delete()
        return redirect('vendor_dashboard')  

    
    return render(request, 'vendor_delete_equipment.html', {'equipment': equipment})

@login_required
def manage_bookings(request):
    bookings = Booking.objects.filter(equipment__vendor=request.user.vendorprofile)
    paginator = Paginator(bookings, 8)
    page_number = request.GET.get('page')
    bookings = paginator.get_page(page_number)
    return render(request, 'vendor_manage_bookings.html', {'bookings': bookings})

@login_required
def approve_booking(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id, equipment__vendor=request.user.vendorprofile)
    booking.status = 'approved'
    booking.save()
    return redirect('manage_bookings')
@login_required
def decline_booking(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id, equipment__vendor=request.user.vendorprofile)
    booking.status = 'declined'
    booking.save()
    return redirect('manage_bookings')
# @login_required
# def earnings(request):
#     transactions = Transaction.objects.filter(vendor=request.user.vendorprofile)
#     print(transactions)
#     return render(request, 'vendor_earnings.html', {'transactions': transactions})
@login_required
def earnings(request):
    transactions = Transaction.objects.filter(vendor=request.user.vendorprofile)
    total_earnings = transactions.aggregate(total=models.Sum('amount'))['total'] or 0
    return render(request, 'vendor_earnings.html', {
        'transactions': transactions,
        'total_earnings': total_earnings
    })

@login_required
def view_reviews(request):
    reviews = Review.objects.filter(equipment__vendor=request.user.vendorprofile)
    return render(request, 'vendor_view_reviews.html', {'reviews': reviews})


def vendor_logout(request):
    logout(request)
    return redirect('index')

@login_required
def create_delivery_zone(request):
    if request.method == 'POST':
        form = DeliveryZoneForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('manage_delivery_zone')
    else:
        form = DeliveryZoneForm()
    return render(request, 'create_delivery_zone.html', {'form': form})

@login_required
def manage_delivery_zone(request):
    zones = DeliveryZone.objects.all()
    return render(request, 'manage_delivery_zone.html', {'zones': zones})

@login_required
def update_delivery_zone(request, zone_id):
    zone = get_object_or_404(DeliveryZone, id=zone_id)
    if request.method == 'POST':
        form = DeliveryZoneForm(request.POST, instance=zone)
        if form.is_valid():
            form.save()
            return redirect('manage_delivery_zone')  # Redirect to the delivery zones list
    else:
        form = DeliveryZoneForm(instance=zone)
    return render(request, 'update_delivery_zone.html', {'form': form, 'zone': zone})

@login_required
def create_restricted_area(request):
    if request.method == 'POST':
        form = RestrictedAreaForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('manage_restricted_area')  # Redirect to the restricted areas list
    else:
        form = RestrictedAreaForm()
    return render(request, 'create_restricted_area.html', {'form': form})
@login_required
def manage_restricted_area(request):
    areas = RestrictedArea.objects.all()
    return render(request, 'manage_restricted_area.html', {'areas': areas})
@login_required
def update_restricted_area(request, area_id):
    area = get_object_or_404(RestrictedArea, id=area_id)
    if request.method == 'POST':
        form = RestrictedAreaForm(request.POST, instance=area)
        if form.is_valid():
            form.save()
            return redirect('manage_restricted_area')  # Redirect to the restricted areas list
    else:
        form = RestrictedAreaForm(instance=area)
    return render(request, 'update_restricted_area.html', {'form': form, 'area': area})
@login_required
def check_delivery_eligibility(request):
    if request.method == 'POST':
        form = DeliveryRequestForm(request.POST)
        if form.is_valid():
            delivery_request = form.save(commit=False)
            delivery_request.user = request.user
            delivery_address = form.cleaned_data['delivery_address']

            # Check if the address is in a restricted area
            restricted_area = RestrictedArea.objects.filter(city__icontains=delivery_address).first()
            if restricted_area:
                delivery_request.is_eligible = False
                delivery_request.status = 'denied'
            else:
                # Check if the address is in a delivery zone
                delivery_zone = DeliveryZone.objects.filter(city__icontains=delivery_address).first()
                if delivery_zone:
                    delivery_request.delivery_zone = delivery_zone
                    delivery_request.delivery_fee = delivery_zone.delivery_fee
                    delivery_request.is_eligible = True
                    delivery_request.status = 'approved'
                else:
                    delivery_request.is_eligible = False
                    delivery_request.status = 'denied'

            delivery_request.save()
            return redirect('delivery_status', delivery_request.id)
    else:
        form = DeliveryRequestForm()
    return render(request, 'check_delivery_eligibility.html', {'form': form})

@login_required
def delivery_status(request, delivery_id):
    delivery_request = get_object_or_404(DeliveryRequest, id=delivery_id, user=request.user)
    return render(request, 'delivery_status.html', {'delivery_request': delivery_request})

