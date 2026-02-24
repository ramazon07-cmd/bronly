import random
from datetime import datetime, timedelta
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone
from django.utils.text import slugify
from django.contrib.auth import get_user_model
from faker import Faker
from apps.users.models import RestaurantOwner, Customer
from apps.restaurants.models import Restaurant, Table
from apps.reservations.models import Reservation

User = get_user_model()


class Command(BaseCommand):
    help = 'Seed database with realistic restaurant reservation data'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--restaurants',
            type=int,
            default=25,
            help='Number of restaurants to create (default: 25)'
        )
        parser.add_argument(
            '--reservations',
            type=int,
            default=350,
            help='Number of reservations to create (default: 350)'
        )
        parser.add_argument(
            '--customers',
            type=int,
            default=50,
            help='Number of customers to create (default: 50)'
        )
    
    def handle(self, *args, **options):
        restaurants_count = options['restaurants']
        reservations_count = options['reservations']
        customers_count = options['customers']
        
        self.stdout.write(self.style.SUCCESS('🚀 Starting BRONLY data seeding...'))
        
        with transaction.atomic():
            # Create restaurant owners
            owners = self.create_owners(5)
            
            # Create customers
            customers = self.create_customers(customers_count)
            
            # Create restaurants
            restaurants = self.create_restaurants(restaurants_count, owners)
            
            # Create tables
            tables = self.create_tables(restaurants)
            
            # Create reservations
            self.create_reservations(reservations_count, tables, customers)
        
        self.stdout.write(self.style.SUCCESS('✅ Data seeding completed successfully!'))
    
    def create_owners(self, count):
        """Create restaurant owners with realistic profiles."""
        self.stdout.write(f'Creating {count} restaurant owners...')
        fake = Faker()
        owners = []
        
        for i in range(count):
            # Create user
            username = fake.unique.user_name()
            user = User.objects.create_user(
                username=username,
                email=f"{username}@owner.com",
                password="password123",
                first_name=fake.first_name(),
                last_name=fake.last_name(),
                phone=fake.phone_number()[:20]
            )
            
            # Create owner profile
            owner = RestaurantOwner.objects.create(
                user=user,
                business_license=fake.bothify(text="LIC-######")
            )
            owners.append(owner)
        
        self.stdout.write(self.style.SUCCESS(f'✅ Created {len(owners)} restaurant owners'))
        return owners
    
    def create_customers(self, count):
        """Create customers with realistic profiles."""
        self.stdout.write(f'Creating {count} customers...')
        fake = Faker()
        customers = []
        
        for i in range(count):
            # Create user
            username = fake.unique.user_name()
            user = User.objects.create_user(
                username=username,
                email=f"{username}@customer.com",
                password="password123",
                first_name=fake.first_name(),
                last_name=fake.last_name(),
                phone=fake.phone_number()[:20]
            )
            
            # Create customer profile
            customer = Customer.objects.create(
                user=user,
                dietary_preferences=random.choice([
                    "No preferences",
                    "Vegetarian",
                    "Vegan",
                    "Gluten-free",
                    "Lactose intolerant",
                    "Nut allergies",
                    "Seafood allergies"
                ])
            )
            customers.append(customer)
        
        self.stdout.write(self.style.SUCCESS(f'✅ Created {len(customers)} customers'))
        return customers
    
    def create_restaurants(self, count, owners):
        """Create restaurants with realistic data."""
        self.stdout.write(f'Creating {count} restaurants...')
        fake = Faker()
        restaurants = []
        
        # Popular cuisine types
        cuisine_choices = [
            "italian", "chinese", "indian", "mexican", "japanese",
            "french", "american", "thai", "korean", "vietnamese",
            "turkish", "seafood", "vegan", "fusion"
        ]
        
        # Popular time slots
        opening_times = [8, 9, 10, 11]  # 8 AM to 11 AM
        closing_times = [20, 21, 22, 23]  # 8 PM to 11 PM
        
        existing_slugs = set(Restaurant.objects.values_list('slug', flat=True))
        
        for i in range(count):
            owner = random.choice(owners)
            cuisine = random.choice(cuisine_choices)
            
            # Generate unique restaurant name
            name = fake.company() + " Restaurant"
            
            # Generate unique slug
            base_slug = slugify(name)
            slug = base_slug
            counter = 1
            
            while slug in existing_slugs or Restaurant.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            
            existing_slugs.add(slug)
            
            restaurant = Restaurant(
                owner=owner.user,
                name=name,
                slug=slug,
                description=fake.paragraph(nb_sentences=3),
                cuisine_type=cuisine,
                phone=fake.phone_number()[:20],
                email=fake.company_email(),
                website=f"https://www.{fake.domain_word()}.com",
                address=fake.street_address(),
                city=fake.city(),
                postal_code=fake.postcode(),
                latitude=float(fake.latitude()),
                longitude=float(fake.longitude()),
                opening_time=timezone.make_aware(
                    datetime.combine(datetime.today(), 
                                    datetime.min.time().replace(hour=random.choice(opening_times)))
                ).time(),
                closing_time=timezone.make_aware(
                    datetime.combine(datetime.today(), 
                                    datetime.min.time().replace(hour=random.choice(closing_times)))
                ).time(),
                is_active=True
            )
            restaurants.append(restaurant)
        
        # Bulk create restaurants
        created_restaurants = Restaurant.objects.bulk_create(restaurants)
        self.stdout.write(self.style.SUCCESS(f'✅ Created {len(created_restaurants)} restaurants'))
        return created_restaurants
    
    def create_tables(self, restaurants):
        """Create 10 tables per restaurant."""
        self.stdout.write('Creating tables for restaurants...')
        tables = []
        
        for restaurant in restaurants:
            for i in range(1, 11):  # 10 tables per restaurant
                table = Table(
                    restaurant=restaurant,
                    table_number=f"Table-{i:02d}",
                    capacity=random.choice([2, 4, 6, 8]),
                    description=f"Table {i} in {restaurant.name}",
                    is_active=True
                )
                tables.append(table)
        
        # Bulk create tables
        created_tables = Table.objects.bulk_create(tables)
        self.stdout.write(self.style.SUCCESS(f'✅ Created {len(created_tables)} tables'))
        return created_tables
    
    def create_reservations(self, count, tables, customers):
        """Create reservations with proper validation."""
        self.stdout.write(f'Creating {count} reservations...')
        fake = Faker()
        reservations = []
        
        # Available time slots (popular dining hours)
        time_slots = [
            "12:00", "12:30", "13:00", "13:30",
            "18:00", "18:30", "19:00", "19:30", "20:00"
        ]
        
        # Status weights for realistic distribution
        status_weights = ['pending', 'confirmed', 'cancelled', 'completed']
        status_distribution = [0.3, 0.5, 0.1, 0.1]  # 30% pending, 50% confirmed, etc.
        
        # Generate future dates (next 90 days)
        today = timezone.now().date()
        future_dates = [
            today + timedelta(days=i) 
            for i in range(1, 91)  # Next 3 months
        ]
        
        created_count = 0
        attempts = 0
        max_attempts = count * 3  # Allow some failed attempts due to conflicts
        
        while created_count < count and attempts < max_attempts:
            attempts += 1
            
            # Random selection
            table = random.choice(tables)
            customer = random.choice(customers)
            date = random.choice(future_dates)
            time_str = random.choice(time_slots)
            guest_count = random.randint(1, min(table.capacity, 8))
            
            # Parse time
            reservation_time = datetime.strptime(time_str, "%H:%M").time()
            
            # Check for conflicts (double booking prevention)
            conflict_exists = Reservation.objects.filter(
                table=table,
                reservation_date=date,
                reservation_time=reservation_time,
                status__in=['pending', 'confirmed']
            ).exists()
            
            if conflict_exists:
                continue  # Skip this attempt, try another combination
            
            # Create reservation
            status = random.choices(status_weights, status_distribution)[0]
            
            reservation = Reservation(
                customer=customer.user,
                table=table,
                reservation_date=date,
                reservation_time=reservation_time,
                guest_count=guest_count,
                special_requests=fake.paragraph(nb_sentences=1) if random.random() > 0.7 else "",
                status=status
            )
            reservations.append(reservation)
            created_count += 1
            
            # Batch insert every 100 reservations for performance
            if len(reservations) >= 100:
                Reservation.objects.bulk_create(reservations)
                self.stdout.write(f'  Progress: {created_count}/{count} reservations created')
                reservations = []
        
        # Create remaining reservations
        if reservations:
            Reservation.objects.bulk_create(reservations)
        
        self.stdout.write(self.style.SUCCESS(f'✅ Created {created_count} reservations'))