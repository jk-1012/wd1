from django.contrib.auth.models import AbstractUser, Group, Permission
from django.db import models
from django.core.exceptions import ValidationError


class User(AbstractUser):
    email = models.EmailField(unique=True)
    mobile_no = models.CharField(max_length=15, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

     # Use email as the unique identifier
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']  # Username is still required for user creation

    def __str__(self):
        return self.email


# 2. Bus Details Table
class Bus(models.Model):
    operator_name = models.CharField(max_length=100)
    source = models.CharField(max_length=100)
    destination = models.CharField(max_length=100)
    departure_time = models.TimeField()
    arrival_time = models.TimeField()
    class_type = models.CharField(max_length=50)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    travel_date = models.DateField()
    total_seats = models.IntegerField()

# 3. Train Details Table
class Train(models.Model):
    train_name = models.CharField(max_length=100)
    source = models.CharField(max_length=100)
    destination = models.CharField(max_length=100)
    departure_time = models.TimeField()
    arrival_time = models.TimeField()
    class_type = models.CharField(max_length=50)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    travel_date = models.DateField()
    total_seats = models.IntegerField()

# 4. Flight Details Table
class Flight(models.Model):
    airline_name = models.CharField(max_length=100)
    source = models.CharField(max_length=100)
    destination = models.CharField(max_length=100)
    departure_time = models.TimeField()
    arrival_time = models.TimeField()
    class_type = models.CharField(max_length=50)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    travel_date = models.DateField()
    total_seats = models.IntegerField()

# 5. Seat Availability Table
class SeatAvailability(models.Model):
    STATUS_CHOICES = [
        ('available', 'Available'),
        ('booked', 'Booked'),
    ]
    BERTH_CHOICES = [
        ('lower-left', 'Lower Left'),
        ('lower-right', 'Lower Right'),
        ('upper-left', 'Upper Left'),
        ('upper-right', 'Upper Right'),
    ]

    bus = models.ForeignKey(Bus, null=True, blank=True, on_delete=models.CASCADE, related_name="seats")
    train = models.ForeignKey(Train, null=True, blank=True, on_delete=models.CASCADE, related_name="seats")
    flight = models.ForeignKey(Flight, null=True, blank=True, on_delete=models.CASCADE, related_name="seats")
    seat_number = models.CharField(max_length=10)
    berth = models.CharField(max_length=20, choices=BERTH_CHOICES, default='lower-left')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='available')
    booking = models.ForeignKey('Booking', null=True, blank=True, on_delete=models.SET_NULL)

    def __str__(self):
        if self.bus:
            return f"Bus Seat {self.seat_number} ({self.bus})"
        elif self.train:
            return f"Train Seat {self.seat_number} ({self.train})"
        elif self.flight:
            return f"Flight Seat {self.seat_number} ({self.flight})"
        else:
            return f"Seat {self.seat_number} (Unknown Vehicle)"



# 6. Bookings Table
class Booking(models.Model):
    VEHICLE_TYPE_CHOICES = [
        ('bus', 'Bus'),
        ('train', 'Train'),
        ('flight', 'Flight'),
    ]
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('cancelled', 'Cancelled'),
        ('paid', 'Paid'),  # Add 'paid' status
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    vehicle_type = models.CharField(max_length=10, choices=VEHICLE_TYPE_CHOICES)
    vehicle_id = models.IntegerField()
    seat_numbers = models.CharField(max_length=100)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    booking_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')


    def get_travel_object(self):
        if self.vehicle_type == 'bus':
            return Bus.objects.get(pk=self.vehicle_id)
        elif self.vehicle_type == 'train':
            return Train.objects.get(pk=self.vehicle_id)
        elif self.vehicle_type == 'flight':
            return Flight.objects.get(pk=self.vehicle_id)
        return None

    def __str__(self):
        return f"Booking {self.id} - {self.user.username} - {self.vehicle_type}"
    def clean(self):
        # Ensure the total price is at least ₹1.00
        if self.total_price < 1.00:
            raise ValidationError("Total price must be at least ₹1.00.")
    
    #def __str__(self):
        return f"Booking {self.id} - {self.user.username} - {self.vehicle_type}"
    
    
# 7. Passenger Details Table
class PassengerDetail(models.Model):
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    age = models.IntegerField()
    mobile_no = models.CharField(max_length=15, null=True, blank=True)

# 8. Payments Table
class Payment(models.Model):
    booking = models.OneToOneField(Booking, on_delete=models.CASCADE)
    razorpay_order_id = models.CharField(max_length=100, unique=True, default="default_order_id")
    razorpay_payment_id = models.CharField(max_length=100, null=True, blank=True)
    razorpay_signature = models.CharField(max_length=255, null=True, blank=True)
    status = models.CharField(max_length=50, choices=[('pending', 'Pending'), ('success', 'Success'), ('failed', 'Failed')], default='pending')

    def __str__(self):
        return f"Payment for {self.booking}"
    

class City(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class Attraction(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField()
    image_url = models.URLField()
    link = models.URLField()
    city = models.ForeignKey(City, on_delete=models.CASCADE, related_name='attractions')

    def __str__(self):
        return self.name
    
class BusDriver(models.Model):
    bus = models.ForeignKey(Bus, on_delete=models.CASCADE, related_name='drivers')
    name = models.CharField(max_length=100)
    age = models.IntegerField()
    license_number = models.CharField(max_length=20)
    license_expiry = models.DateField()
    experience_years = models.IntegerField()
    rating = models.IntegerField(default=4)  # 1-5 scale

class TrainCrew(models.Model):
    train = models.ForeignKey(Train, on_delete=models.CASCADE, related_name='crew')
    name = models.CharField(max_length=100)
    age = models.IntegerField()
    role = models.CharField(max_length=50)  # 'driver', 'manager', etc.
    experience_years = models.IntegerField()

class FlightCrew(models.Model):
    flight = models.ForeignKey(Flight, on_delete=models.CASCADE, related_name='crew')
    name = models.CharField(max_length=100)
    age = models.IntegerField()
    role = models.CharField(max_length=50)  # 'captain', 'first officer', etc.
    experience_years = models.IntegerField()