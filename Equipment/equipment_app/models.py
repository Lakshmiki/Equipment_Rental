from django.db import models
from django.contrib.auth.models import AbstractUser,Permission,Group,User


# class User(AbstractUser):
#     ROLE_CHOICES = (
#         ('admin', 'Admin'),
#         ('vendor', 'Vendor'),
#         ('user', 'User'),
#         ('delivery', 'Delivery'),
#     )
#     role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='user')
#     is_verified = models.BooleanField(default=False)
#     groups = models.ManyToManyField(Group, related_name="custom_user_set", blank=True)
#     user_permissions = models.ManyToManyField(Permission, related_name="custom_user_permissions_set", blank=True)

#     def __str__(self):
#         return self.username



# Create your models here.
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone_number = models.CharField(max_length=15)
    address = models.TextField()  
    is_verified = models.BooleanField(default=False)
    id_proof = models.FileField(upload_to='id_proofs/', null=True, blank=True)

    def __str__(self):
        return self.user.username
    
class VendorProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    company_name = models.CharField(max_length=255)
    description = models.TextField()
    phone_number = models.CharField(max_length=15)
    business_license = models.FileField(upload_to='business_licenses/')
    is_approved = models.BooleanField(default=False)
    payment_details = models.JSONField(default=dict) 

    def __str__(self):
        return self.company_name

class Equipment(models.Model):
    vendor = models.ForeignKey(VendorProfile, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    category = models.CharField(max_length=100)
    specifications = models.TextField()
    price_per_hour = models.DecimalField(max_digits=10, decimal_places=2)
    price_per_day = models.DecimalField(max_digits=10, decimal_places=2)
    price_per_week = models.DecimalField(max_digits=10, decimal_places=2)
    is_available = models.BooleanField(default=True)
    is_not_available = models.BooleanField(default=False)
    is_approved = models.BooleanField(default=False)
    images = models.ImageField(upload_to='equipment_images/')

    def __str__(self):
        return self.name
    
class Booking(models.Model):
    equipment = models.ForeignKey(Equipment, on_delete=models.CASCADE)
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    total_cost = models.DecimalField(max_digits=10, decimal_places=2)
    payment_status = models.CharField(max_length=20, choices=[
        ('pending', 'Pending'),
        ('partial', 'Partial'),
        ('full', 'Full'),
    ])
    booking_status = models.CharField(max_length=20, choices=[
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('dispatched', 'Dispatched'),
        ('delivered', 'Delivered'),
        ('canceled', 'Canceled'),
    ],default='pending' )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Booking {self.id} for {self.equipment.name}"
    
class Report(models.Model):
    report_type = models.CharField(max_length=50)
    generated_at = models.DateTimeField(auto_now_add=True)
    data = models.JSONField()

    def __str__(self):
        return f"{self.report_type} Report"

class PlatformSettings(models.Model):
    rental_pricing = models.JSONField()
    commission_rate = models.DecimalField(max_digits=5, decimal_places=2)
    promotional_campaigns = models.JSONField()
    email_settings = models.JSONField()
    booking_rules = models.TextField()

    def __str__(self):
        return "Platform Settings"

class Review(models.Model):
    equipment = models.ForeignKey(Equipment, on_delete=models.CASCADE)
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    rating = models.IntegerField(choices=[(i, i) for i in range(1, 6)])
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Review by {self.user.user.username} for {self.equipment.name}"
class DeliveryZone(models.Model):
    zone_name = models.CharField(max_length=100)
    city = models.CharField(max_length=100)
    zip_code = models.CharField(max_length=10)
    is_active = models.BooleanField(default=True)
    delivery_fee = models.DecimalField(max_digits=6, decimal_places=2)

    def __str__(self):
        return self.zone_name

class RestrictedArea(models.Model):
    area_name = models.CharField(max_length=100)
    city = models.CharField(max_length=100)
    zip_code = models.CharField(max_length=10)
    reason = models.TextField()

    def __str__(self):
        return self.area_name
    
class DeliveryRequest(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    delivery_address = models.CharField(max_length=255)
    delivery_zone = models.ForeignKey(DeliveryZone, on_delete=models.SET_NULL, null=True, blank=True)
    is_eligible = models.BooleanField(default=False)
    delivery_fee = models.DecimalField(max_digits=6, decimal_places=2, default=0.0)
    status = models.CharField(max_length=20, choices=[
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('denied', 'Denied'),
    ])
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Delivery Request {self.id} by {self.user.username}"

class Transaction(models.Model):
    vendor = models.ForeignKey(VendorProfile, on_delete=models.CASCADE)
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=[
        ('pending', 'Pending'),
        ('completed', 'Completed'),
    ])
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Transaction {self.id} for {self.vendor.company_name}"
    
