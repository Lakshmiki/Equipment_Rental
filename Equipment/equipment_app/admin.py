from django.contrib import admin
from .models import *

# Register your models here.
admin.site.register(Booking)
admin.site.register(UserProfile)
admin.site.register(VendorProfile)
admin.site.register(Equipment)
admin.site.register(Avail_Location)
admin.site.register(DeliveryLocation)
admin.site.register(Report)
admin.site.register(Platform_Settings)
admin.site.register(Review)
admin.site.register(DeliveryZone)
admin.site.register(RestrictedArea)
admin.site.register(DeliveryRequest)
admin.site.register(Transaction)