from django import forms
from django.core.exceptions import ValidationError
from datetime import datetime, time
from .models import Restaurant, Table
from apps.reservations.models import Reservation


class RestaurantForm(forms.ModelForm):
    """Form for creating and updating restaurants (slug auto-generated)."""

    class Meta:
        model = Restaurant
        fields = [
            'name', 'description', 'cuisine_type',
            'phone', 'email', 'website',
            'address', 'city', 'postal_code',
            'opening_time', 'closing_time',
            'logo', 'cover_image'
        ]
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Restaurant Name'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Description'}),
            'cuisine_type': forms.Select(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'type': 'tel', 'placeholder': '+1-555-0000'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'email@restaurant.com'}),
            'website': forms.URLInput(attrs={'class': 'form-control', 'required': False}),
            'address': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Street address'}),
            'city': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'City'}),
            'postal_code': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Postal Code'}),
            'opening_time': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'closing_time': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'logo': forms.FileInput(attrs={'class': 'form-control', 'accept': 'image/*'}),
            'cover_image': forms.FileInput(attrs={'class': 'form-control', 'accept': 'image/*'}),
        }

    def clean_name(self):
        """Validate restaurant name is not empty and reasonable length."""
        name = self.cleaned_data.get('name', '').strip()
        if not name:
            raise ValidationError('Restaurant name is required.')
        if len(name) < 2:
            raise ValidationError('Restaurant name must be at least 2 characters.')
        if len(name) > 200:
            raise ValidationError('Restaurant name cannot exceed 200 characters.')
        return name

    def clean_phone(self):
        """Validate phone number format."""
        phone = self.cleaned_data.get('phone', '').strip()
        if not phone:
            raise ValidationError('Phone number is required.')
        # Remove common formatting characters and check length
        cleaned_phone = ''.join(c for c in phone if c.isdigit())
        if len(cleaned_phone) < 10:
            raise ValidationError('Phone number must be at least 10 digits.')
        return phone

    def clean_email(self):
        """Validate email is unique and properly formatted."""
        email = self.cleaned_data.get('email', '').strip()
        if not email:
            raise ValidationError('Email is required.')
        # Check for duplicate email (exclude current instance if editing)
        existing = Restaurant.objects.filter(email=email)
        if self.instance.pk:
            existing = existing.exclude(pk=self.instance.pk)
        if existing.exists():
            raise ValidationError('This email is already registered.')
        return email

    def clean(self):
        """Validate opening and closing times."""
        cleaned_data = super().clean()
        opening_time = cleaned_data.get('opening_time')
        closing_time = cleaned_data.get('closing_time')

        if opening_time and closing_time:
            if closing_time <= opening_time:
                raise ValidationError('Closing time must be after opening time.')

        return cleaned_data

    def clean_logo(self):
        """Validate logo file size (max 2MB)."""
        logo = self.cleaned_data.get('logo')
        if logo and logo.size > 2 * 1024 * 1024:
            raise ValidationError('Logo file size must not exceed 2MB.')
        return logo

    def clean_cover_image(self):
        """Validate cover image file size (max 5MB)."""
        cover_image = self.cleaned_data.get('cover_image')
        if cover_image and cover_image.size > 5 * 1024 * 1024:
            raise ValidationError('Cover image file size must not exceed 5MB.')
        return cover_image


class TableForm(forms.ModelForm):
    """Form for creating and updating tables."""

    class Meta:
        model = Table
        fields = ['table_number', 'capacity', 'description']
        widgets = {
            'table_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., A1, Table-1'}),
            'capacity': forms.NumberInput(attrs={'class': 'form-control', 'min': 1, 'max': 20}),
            'description': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., Window seat, Corner table'}),
        }

    def clean_table_number(self):
        """Validate table number is not empty."""
        table_number = self.cleaned_data.get('table_number', '').strip()
        if not table_number:
            raise ValidationError('Table number is required.')
        if len(table_number) > 10:
            raise ValidationError('Table number cannot exceed 10 characters.')
        return table_number

    def clean_capacity(self):
        """Validate table capacity."""
        capacity = self.cleaned_data.get('capacity')
        if not capacity:
            raise ValidationError('Table capacity is required.')
        if capacity < 1:
            raise ValidationError('Table capacity must be at least 1 guest.')
        if capacity > 20:
            raise ValidationError('Table capacity cannot exceed 20 guests.')
        return capacity


class PublicReservationForm(forms.Form):
    """Form for customers to book reservations (with comprehensive validation)."""

    table_id = forms.IntegerField(widget=forms.Select)
    reservation_date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}))
    reservation_time = forms.TimeField(widget=forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}))
    guest_count = forms.IntegerField(
        widget=forms.NumberInput(attrs={'class': 'form-control', 'min': 1, 'max': 20}),
        min_value=1,
        max_value=20
    )
    special_requests = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'e.g., Dietary restrictions, seating preference'})
    )

    def __init__(self, *args, restaurant=None, **kwargs):
        """Initialize form with restaurant context for validation."""
        super().__init__(*args, **kwargs)
        self.restaurant = restaurant

        # Populate table choices dynamically
        if restaurant:
            tables = restaurant.tables.filter(is_active=True).order_by('capacity')
            self.fields['table_id'].widget = forms.Select(
                choices=[(t.id, f"Table {t.table_number} ({t.capacity} guests)") for t in tables],
                attrs={'class': 'form-control'}
            )

    def clean_reservation_date(self):
        """Validate that reservation date is not in the past."""
        date = self.cleaned_data.get('reservation_date')
        if not date:
            raise ValidationError('Reservation date is required.')

        today = datetime.now().date()
        if date < today:
            raise ValidationError('Cannot book reservations in the past. Please select a future date.')

        return date

    def clean_reservation_time(self):
        """Validate time format."""
        time_obj = self.cleaned_data.get('reservation_time')
        if not time_obj:
            raise ValidationError('Reservation time is required.')
        return time_obj

    def clean_guest_count(self):
        """Validate guest count."""
        guest_count = self.cleaned_data.get('guest_count')
        if not guest_count or guest_count < 1:
            raise ValidationError('Guest count must be at least 1.')
        if guest_count > 20:
            raise ValidationError('Guest count cannot exceed 20.')
        return guest_count

    def clean(self):
        """Perform comprehensive validation including overlap and hours."""
        cleaned_data = super().clean()

        table_id = cleaned_data.get('table_id')
        reservation_date = cleaned_data.get('reservation_date')
        reservation_time = cleaned_data.get('reservation_time')
        guest_count = cleaned_data.get('guest_count')

        if not (table_id and reservation_date and reservation_time and guest_count):
            return cleaned_data

        try:
            table = Table.objects.select_related('restaurant').get(
                id=table_id,
                restaurant=self.restaurant,
                is_active=True
            )
        except Table.DoesNotExist:
            raise ValidationError('Selected table is not available.')

        # VALIDATION 1: Check table capacity
        if guest_count > table.capacity:
            self.add_error(
                'guest_count',
                f'This table can accommodate maximum {table.capacity} guests.'
            )

        # VALIDATION 2: Check restaurant operating hours
        restaurant = table.restaurant
        if not (restaurant.opening_time <= reservation_time <= restaurant.closing_time):
            self.add_error(
                'reservation_time',
                f'Restaurant operates from {restaurant.opening_time.strftime("%H:%M")} to {restaurant.closing_time.strftime("%H:%M")}.'
            )

        # VALIDATION 3: Check for booking overlap (no double-booking)
        overlap_exists = Reservation.objects.filter(
            table=table,
            reservation_date=reservation_date,
            reservation_time=reservation_time,
            status__in=['pending', 'confirmed']
        ).exists()

        if overlap_exists:
            self.add_error(
                None,  # Non-field error
                f'Table is already booked for {reservation_time.strftime("%H:%M")} on {reservation_date.strftime("%A, %B %d, %Y")}. Please choose a different time or table.'
            )

        return cleaned_data

    def save(self, commit=True):
        """Create and return Reservation instance."""
        from apps.reservations.models import Reservation

        reservation = Reservation(
            table_id=self.cleaned_data['table_id'],
            reservation_date=self.cleaned_data['reservation_date'],
            reservation_time=self.cleaned_data['reservation_time'],
            guest_count=self.cleaned_data['guest_count'],
            special_requests=self.cleaned_data.get('special_requests', ''),
        )

        if commit:
            reservation.save()

        return reservation
