from django import forms
from django.core.exceptions import ValidationError
from datetime import datetime, timedelta
from .models import Reservation
from apps.restaurants.models import Table


class ReservationForm(forms.ModelForm):
    """Form for creating and updating reservations with comprehensive validation."""
    
    class Meta:
        model = Reservation
        fields = ['table', 'reservation_date', 'reservation_time', 'guest_count', 'special_requests']
        widgets = {
            'table': forms.Select(attrs={'class': 'form-control'}),
            'reservation_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'reservation_time': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
            'guest_count': forms.NumberInput(attrs={'class': 'form-control', 'min': 1, 'max': 20}),
            'special_requests': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Special requests or dietary restrictions'})
        }

    def __init__(self, *args, restaurant=None, **kwargs):
        """Initialize form with restaurant context for validation."""
        super().__init__(*args, **kwargs)
        self.restaurant = restaurant
        
        # Filter tables by restaurant if provided
        if restaurant:
            self.fields['table'].queryset = restaurant.tables.filter(is_active=True).order_by('table_number')

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

    def clean_table(self):
        """Validate that the selected table belongs to the restaurant."""
        table = self.cleaned_data.get('table')
        if not table:
            raise ValidationError('Please select a table.')
        
        if self.restaurant and table.restaurant != self.restaurant:
            raise ValidationError('Selected table does not belong to this restaurant.')
        
        return table

    def clean(self):
        """Perform comprehensive validation including time-based overlap detection and hours."""
        cleaned_data = super().clean()

        table = cleaned_data.get('table')
        reservation_date = cleaned_data.get('reservation_date')
        reservation_time = cleaned_data.get('reservation_time')
        guest_count = cleaned_data.get('guest_count')

        if not (table and reservation_date and reservation_time and guest_count):
            return cleaned_data

        # VALIDATION 1: Check table capacity
        if guest_count > table.capacity:
            raise ValidationError({
                'guest_count': f'This table can accommodate maximum {table.capacity} guests. Please select a larger table or reduce guest count.'
            })

        # VALIDATION 2: Check restaurant operating hours
        restaurant = table.restaurant
        if not (restaurant.opening_time <= reservation_time <= restaurant.closing_time):
            raise ValidationError({
                'reservation_time': f'Restaurant operates from {restaurant.opening_time.strftime("%H:%M")} to {restaurant.closing_time.strftime("%H:%M")}. Please select a time within operating hours.'
            })

        # VALIDATION 3: Time-based conflict detection (2-hour windows)
        if not self._check_time_conflicts(table, reservation_date, reservation_time):
            raise ValidationError('This time slot is not available for this table. Please choose a different time (2-hour window conflict detected).')

        return cleaned_data

    def _check_time_conflicts(self, table, reservation_date, reservation_time):
        """Check for time-based conflicts using 2-hour windows."""
        from datetime import datetime, timedelta
        from django.db.models import Q
        
        # Create datetime objects for the new reservation
        new_reservation_start = datetime.combine(reservation_date, reservation_time)
        new_reservation_end = new_reservation_start + timedelta(hours=2)
        
        # Query existing reservations with time overlap
        existing_reservations = Reservation.objects.filter(
            table=table,
            reservation_date=reservation_date,
            status__in=['pending', 'confirmed']
        )
        
        # Check each existing reservation for time overlap
        for existing_reservation in existing_reservations:
            # Get existing reservation time range
            existing_start = datetime.combine(
                existing_reservation.reservation_date,
                existing_reservation.reservation_time
            )
            existing_end = existing_start + timedelta(hours=2)
            
            # Check for overlap: (StartA < EndB) and (EndA > StartB)
            if (new_reservation_start < existing_end) and (new_reservation_end > existing_start):
                return False  # Conflict found
        
        return True  # No conflicts


class ReservationStatusForm(forms.ModelForm):
    """Form for updating reservation status (for restaurant owners)."""
    
    class Meta:
        model = Reservation
        fields = ['status']
        widgets = {
            'status': forms.Select(attrs={'class': 'form-control'})
        }


class AvailabilityCheckForm(forms.Form):
    """Form for checking table availability via AJAX."""
    
    table_id = forms.IntegerField()
    reservation_date = forms.DateField()
    reservation_time = forms.TimeField()
    
    def clean_table_id(self):
        """Validate table exists."""
        table_id = self.cleaned_data.get('table_id')
        try:
            table = Table.objects.get(id=table_id)
        except Table.DoesNotExist:
            raise ValidationError('Selected table does not exist.')
        return table_id
    
    def clean_reservation_date(self):
        """Validate that reservation date is not in the past."""
        date = self.cleaned_data.get('reservation_date')
        if not date:
            raise ValidationError('Reservation date is required.')

        today = datetime.now().date()
        if date < today:
            raise ValidationError('Cannot check availability for past dates.')

        return date

    def clean(self):
        """Check availability for the given table and time."""
        cleaned_data = super().clean()
        
        table_id = cleaned_data.get('table_id')
        reservation_date = cleaned_data.get('reservation_date')
        reservation_time = cleaned_data.get('reservation_time')
        
        if not (table_id and reservation_date and reservation_time):
            return cleaned_data
            
        try:
            table = Table.objects.get(id=table_id)
        except Table.DoesNotExist:
            raise ValidationError({'table_id': 'Selected table does not exist.'})
        
        # Check restaurant operating hours
        restaurant = table.restaurant
        if not (restaurant.opening_time <= reservation_time <= restaurant.closing_time):
            raise ValidationError({
                'reservation_time': f'Restaurant operates from {restaurant.opening_time.strftime("%H:%M")} to {restaurant.closing_time.strftime("%H:%M")}.'
            })
        
        # Check availability
        is_available = self._check_availability(table, reservation_date, reservation_time)
        if not is_available:
            raise ValidationError('Selected time slot is not available.')
        
        return cleaned_data
    
    def _check_availability(self, table, reservation_date, reservation_time):
        """Check if the table is available at the given time."""
        from datetime import datetime, timedelta
        from django.db.models import Q
        
        # Create datetime objects for the requested reservation
        new_reservation_start = datetime.combine(reservation_date, reservation_time)
        new_reservation_end = new_reservation_start + timedelta(hours=2)
        
        # Query existing reservations with time overlap
        existing_reservations = Reservation.objects.filter(
            table=table,
            reservation_date=reservation_date,
            status__in=['pending', 'confirmed']
        )
        
        # Check each existing reservation for time overlap
        for existing_reservation in existing_reservations:
            # Get existing reservation time range
            existing_start = datetime.combine(
                existing_reservation.reservation_date,
                existing_reservation.reservation_time
            )
            existing_end = existing_start + timedelta(hours=2)
            
            # Check for overlap: (StartA < EndB) and (EndA > StartB)
            if (new_reservation_start < existing_end) and (new_reservation_end > existing_start):
                return False  # Conflict found
        
        return True  # Available