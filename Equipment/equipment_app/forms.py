from django import forms
from .models import UserProfile,VendorProfile,Equipment,Booking,Report,Platform_Settings,Review,DeliveryZone,RestrictedArea,DeliveryRequest,Avail_Location,DeliveryLocation
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.core.exceptions import ValidationError
from datetime import date,datetime
from django.core.validators import RegexValidator
from django.contrib.auth import authenticate, login


class UserRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    phone_number = forms.CharField(max_length=15, required=True)
    address = forms.CharField(widget=forms.Textarea, required=True)
    id_proof = forms.FileField(required=False)

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2', 'phone_number', 'address', 'id_proof']

# class UserLoginForm(AuthenticationForm):
#     username = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Username'}))
#     password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Password'}))
class UserLoginForm(AuthenticationForm):
    username = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Password'}))

    def clean(self):
        email = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')
        if email and password:
            try:
                user = User.objects.get(email=email)
                username = user.username
                authenticated_user = authenticate(username=username, password=password)
                if authenticated_user is None:
                    raise forms.ValidationError("Invalid email or password.")
            except User.DoesNotExist:
                raise forms.ValidationError("Invalid email or password.")
        return self.cleaned_data
# class UserProfileForm(forms.ModelForm):
#     class Meta:
#         model = UserProfile
#         fields = ['phone_number', 'address','id_proof']
#         widgets = {
#             'phone_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter your phone number'}),
#             'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Enter your address'}),

#             'id_proof': forms.FileInput(attrs={'class': 'form-control'}),
#         }
class UserProfileForm(forms.ModelForm):
    phone_number = forms.CharField(
        validators=[
            RegexValidator(
                regex=r'^\+?1?\d{9,15}$', 
                message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed."
            )
        ],
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter your phone number'})
    )
    id_proof = forms.FileField(
        widget=forms.FileInput(attrs={'class': 'form-control'}),
        required=False
    )

    class Meta:
        model = UserProfile
        fields = ['phone_number', 'address', 'id_proof']
        widgets = {
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Enter your address'}),
        }
        def clean_id_proof(self):
            id_proof = self.cleaned_data.get('id_proof')
            if id_proof:
                allowed_types = ['image/jpeg', 'image/png', 'application/pdf']
            if id_proof.content_type not in allowed_types:
                raise forms.ValidationError("Only PDF, JPG, and PNG files are allowed.")
            return id_proof

class VendorRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    company_name = forms.CharField(max_length=255, required=True)
    description = forms.CharField(widget=forms.Textarea, required=True)
    phone_number = forms.CharField(max_length=15, required=True)
    business_license = forms.FileField(required=True)


    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2', 'company_name', 'description', 'phone_number', 'business_license']
# class VendorLoginForm(forms.Form):
#     username = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Username'}))
#     password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Password'}))
class VendorLoginForm(AuthenticationForm):
    username = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Password'}))

    def clean(self):
        email = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')
        if email and password:
            try:
                user = User.objects.get(email=email)
                username = user.username
                authenticated_user = authenticate(username=username, password=password)
                if authenticated_user is None:
                    raise forms.ValidationError("Invalid email or password.")
            except User.DoesNotExist:
                raise forms.ValidationError("Invalid email or password.")
        return self.cleaned_data

class VendorProfileForm(forms.ModelForm):
    class Meta:
        model = VendorProfile
        fields = ['company_name', 'description', 'phone_number', 'payment_details']
        widgets = {
            'company_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter your company name'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Enter your company description'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter your phone number'}),
            'payment_details': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Enter your payment details'}),
        }

class EquipmentForm(forms.ModelForm):
    class Meta:
        model = Equipment
        fields = [
            'vendor', 'name', 'category', 'specifications',
            'price_per_hour', 'price_per_day', 'price_per_week',
            'is_available', 'is_approved', 'images','is_not_available'
        ]
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'category': forms.TextInput(attrs={'class': 'form-control'}),
            'specifications': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'price_per_hour': forms.NumberInput(attrs={'class': 'form-control'}),
            'price_per_day': forms.NumberInput(attrs={'class': 'form-control'}),
            'price_per_week': forms.NumberInput(attrs={'class': 'form-control'}),
            'is_available': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'is_not_available':forms.CheckboxInput(attrs={'class':'form-check-input'}),

            'is_approved': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'images': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }
class AvailableLocationForm(forms.ModelForm):
    class Meta:
        model = Avail_Location
        fields = ['address', 'latitude', 'longitude']

class DeliveryLocationForm(forms.ModelForm):
    class Meta:
        model = DeliveryLocation
        fields = ['address']  # Only include the address field
        widgets = {
            'address': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter delivery address'}),
        }
        labels = {
            'address': 'Delivery Address',
        }

class BookingForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = ['start_date', 'end_date']

    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')

        # Validate that start_date and end_date are provided
        if not start_date or not end_date:
            raise ValidationError("Both start date and end date are required.")

        # Ensure start_date is not in the past
        if datetime.combine(start_date, datetime.min.time()) < datetime.now():
            raise ValidationError("Start date cannot be in the past.")

        # Ensure end_date is not before start_date
        if end_date < start_date:
            raise ValidationError("End date cannot be before the start date.")

        return cleaned_data

class ReportForm(forms.ModelForm):
    class Meta:
        model = Report
        fields = ['report_type', 'data']


class PlatformSettingsForm(forms.ModelForm):
    class Meta:
        model = Platform_Settings
        fields = ['rental_pricing', 'commission_rate', 'promotional_campaigns', 'email_settings', 'booking_rules']

class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['rating', 'comment']
        widgets = {
            'rating': forms.Select(choices=[(i, i) for i in range(1, 6)]),  # Dropdown for rating (1-5)
            'comment': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Write your review here...'}),
        }
        labels = {
            'rating': 'Rating (1-5)',
            'comment': 'Your Review',
        }

class DeliveryZoneForm(forms.ModelForm):
    class Meta:
        model = DeliveryZone
        fields = ['zone_name', 'city', 'zip_code', 'delivery_fee', 'is_active']
        widgets = {
            'zone_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter zone name'}),
            'city': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter city'}),
            'zip_code': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter zip code'}),
            'delivery_fee': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Enter delivery fee'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
        labels = {
            'zone_name': 'Zone Name',
            'city': 'City',
            'zip_code': 'Zip Code',
            'delivery_fee': 'Delivery Fee',
            'is_active': 'Is Active?',
        }

class RestrictedAreaForm(forms.ModelForm):
    class Meta:
        model = RestrictedArea
        fields = ['area_name', 'city', 'zip_code', 'reason']
        widgets = {
            'area_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter area name'}),
            'city': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter city'}),
            'zip_code': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter zip code'}),
            'reason': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Enter reason', 'rows': 4}),
        }
        labels = {
            'area_name': 'Area Name',
            'city': 'City',
            'zip_code': 'Zip Code',
            'reason': 'Reason',
        }
class DeliveryRequestForm(forms.ModelForm):
    class Meta:
        model = DeliveryRequest
        fields = ['delivery_address']