from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login as auth_login
from django.contrib import messages
from .models import Bus, Train, Flight, SeatAvailability, Booking, PassengerDetail, Payment ,City, Attraction,User
from django.http import JsonResponse
from django.conf import settings
import razorpay
from razorpay.errors import SignatureVerificationError
from django.contrib.auth import get_user_model


# Use the custom User model
User = get_user_model()

def book_seats(request, vehicle_type, vehicle_id):
    if request.method == 'POST':
        selected_seats = request.POST.get('selected_seats', '').split(',')
        user_id = request.user.id

        total_price = 0
        for seat_id in selected_seats:
            seat = get_object_or_404(SeatAvailability, id=seat_id, vehicle_type=vehicle_type, vehicle_id=vehicle_id)
            total_price += seat.booking.price

        booking = Booking.objects.create(
            user_id=user_id,
            vehicle_type=vehicle_type,
            vehicle_id=vehicle_id,
            seat_numbers=','.join(selected_seats),
            total_price=total_price,
            status='pending',
        )

        SeatAvailability.objects.filter(id__in=selected_seats).update(status='booked', booking=booking)

        return redirect('info', booking_id=booking.id)
    else:
        return JsonResponse({'error': 'Invalid request method'}, status=400)

def confirm_booking(request, booking_id):
    if request.method == 'POST':
        booking = get_object_or_404(Booking, id=booking_id)

        for seat_number in booking.seat_numbers.split(','):
            PassengerDetail.objects.create(
                booking=booking,
                name=request.POST.get(f'passenger_name_{seat_number}'),
                age=request.POST.get(f'passenger_age_{seat_number}'),
                mobile_no=request.POST.get(f'passenger_mobile_{seat_number}')  # Corrected this line
            )

        booking.status = 'confirmed'
        booking.save()

        return redirect('paymentOption', booking_id=booking.id)
    else:
        return JsonResponse({'error': 'Invalid request method'}, status=400)

def home(request):
    return render(request, 'homepage.html')

def buspage(request):
    return render(request, 'bus.html')

def trainpage(request):
    return render(request, 'train.html')

def flightpage(request):
    return render(request, 'flight.html')

def about(request):
    return render(request, 'aboutus.html')

def signup(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email').lower().strip()  # Convert to lowercase and trim spaces
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')

        if password != confirm_password:
            messages.error(request, "Passwords do not match!")
            return render(request, 'signup.html')

        if User.objects.filter(email=email).exists():
            messages.error(request, "Email is already registered!")
            return render(request, 'signup.html')

        user = User.objects.create_user(username=username, email=email, password=password)
        user.save()
        messages.success(request, "Account created successfully! Please log in.")
        return redirect('login')

    return render(request, 'signup.html')

def login(request):
    if request.method == 'POST':
        email = request.POST.get('email').lower().strip()  # Convert to lowercase and trim spaces
        password = request.POST.get('password')

        user = authenticate(request, username=email, password=password)
        if user is not None:
            auth_login(request, user)
            return redirect('homepage')
        else:
            messages.error(request, "Invalid email or password!")

    return render(request, 'login.html')

def searchplaces(request):
    return render(request, 'SearchPlace.html')

def searchbus(request):
    source = request.GET.get('source')
    destination = request.GET.get('destination')
    travel_date = request.GET.get('travel_date')

    if not travel_date:
        return render(request, 'SearchBus.html', {
            'source': source,
            'destination': destination,
            'travel_date': travel_date,
            'buses': [],
            'error_message': 'Please select a valid travel date.',
        })

    buses = Bus.objects.filter(source=source, destination=destination, travel_date=travel_date)

    return render(request, 'SearchBus.html', {
        'source': source,
        'destination': destination,
        'travel_date': travel_date,
        'buses': buses,
    })

def searchtrain(request):
    source = request.GET.get('source')
    destination = request.GET.get('destination')
    travel_date = request.GET.get('travel_date')

    trains = Train.objects.filter(source=source, destination=destination, travel_date=travel_date)

    return render(request, 'SearchTrain.html', {
        'source': source,
        'destination': destination,
        'travel_date': travel_date,
        'trains': trains,
    })

def searchflight(request):
    source = request.GET.get('source')
    destination = request.GET.get('destination')
    travel_date = request.GET.get('travel_date')

    flights = Flight.objects.filter(source=source, destination=destination, travel_date=travel_date)

    return render(request, 'SearchFlight.html', {
        'source': source,
        'destination': destination,
        'travel_date': travel_date,
        'flights': flights,
    })

# Helper function to calculate seat layout
def get_seat_layout(seat_availability):
    return {
        'Lower Left': seat_availability.filter(berth='lower-left'),
        'Lower Right': seat_availability.filter(berth='lower-right'),
        'Upper Left': seat_availability.filter(berth='upper-left'),
        'Upper Right': seat_availability.filter(berth='upper-right'),
    }

# Select Bus Seat
def selectbusseat(request, bus_id):
    bus = get_object_or_404(Bus, id=bus_id)
    seat_availability = SeatAvailability.objects.filter(bus_id=bus_id)

    if not request.user.is_authenticated:
        return redirect('login')

    selected_seat = seat_availability.filter(status='available').first()
    selected_seat_number = selected_seat.id if selected_seat else None
    
    # Avoid AttributeError for NoneType
    total_price = bus.price if selected_seat else 0.00

    booking = Booking.objects.create(
        user=request.user,
        vehicle_type='bus',
        vehicle_id=bus.id,
        seat_numbers=str(selected_seat_number) if selected_seat_number else '',
        total_price=total_price,
        status='pending',
    )

    if selected_seat:
        selected_seat.status = 'booked'
        selected_seat.booking = booking
        selected_seat.save()

    return render(request, 'SelectBusSeat.html', {
        'bus': bus,
        'seat_layout': get_seat_layout(seat_availability),
        'booking': booking,
    })
#def selectbusseat(request, bus_id):
    bus = get_object_or_404(Bus, pk=bus_id)

    if request.method == 'POST':
        seat_numbers = request.POST.getlist('selected_seats')  # e.g., ['A1', 'A2']
        total_price = float(request.POST.get('total_price', 0))

        seat_string = ",".join(seat_numbers)  # 'A1,A2'

        booking = Booking.objects.create(
            user=request.user,
            vehicle_type='bus',
            vehicle_id=bus.id,
            seat_number=seat_string,
            total_price=total_price,
            status='paid'
        )

        return redirect('booking_success', booking_id=booking.id)

    context = {
        'bus': bus,
    }
    return render(request, 'SelectBusSeat.html', context)

# Select Train Seat
def selecttrainseat(request, train_id):
    train = get_object_or_404(Train, id=train_id)
    seat_availability = SeatAvailability.objects.filter(train_id=train_id)

    if not request.user.is_authenticated:
        return redirect('login')

    selected_seat = seat_availability.filter(status='available').first()
    selected_seat_number = selected_seat.id if selected_seat else None
    total_price = train.price if selected_seat else 0.00

    booking = Booking.objects.create(
        user=request.user,
        vehicle_type='train',
        vehicle_id=train.id,
        seat_numbers=str(selected_seat_number) if selected_seat_number else '',
        total_price=total_price,
        status='pending',
    )

    if selected_seat:
        selected_seat.status = 'booked'
        selected_seat.booking = booking
        selected_seat.save()

    return render(request, 'SelectTrainSeat.html', {
        'train': train,
        'seat_layout': get_seat_layout(seat_availability),
        'booking': booking,
    })
#def selecttrainseat(request, train_id):
    train = get_object_or_404(Train, pk=train_id)

    if request.method == 'POST':
        seat_numbers = request.POST.getlist('selected_seats')
        total_price = float(request.POST.get('total_price', 0))
        seat_string = ",".join(seat_numbers)

        booking = Booking.objects.create(
            user=request.user,
            vehicle_type='train',
            vehicle_id=train.id,
            seat_number=seat_string,
            total_price=total_price,
            status='paid'
        )

        return redirect('booking_success', booking_id=booking.id)

    context = {
        'train': train,
    }
    return render(request, 'SelectTrainSeat.html', context)


# Select Flight Seat
def selectflightseat(request, flight_id):
    flight = get_object_or_404(Flight, id=flight_id)
    seat_availability = SeatAvailability.objects.filter(flight_id=flight_id)

    if not request.user.is_authenticated:
        return redirect('login')

    selected_seat = seat_availability.filter(status='available').first()
    selected_seat_number = selected_seat.id if selected_seat else None
    total_price = flight.price if selected_seat else 0.00

    booking = Booking.objects.create(
        user=request.user,
        vehicle_type='flight',
        vehicle_id=flight.id,
        seat_numbers=str(selected_seat_number) if selected_seat_number else '',
        total_price=total_price,
        status='pending',
    )

    if selected_seat:
        selected_seat.status = 'booked'
        selected_seat.booking = booking
        selected_seat.save()

    return render(request, 'SelectFlightSeat.html', {
        'flight': flight,
        'seat_layout': get_seat_layout(seat_availability),
        'booking': booking,
    })
#def selectflightseat(request, flight_id):
    flight = get_object_or_404(Flight, pk=flight_id)

    if request.method == 'POST':
        seat_numbers = request.POST.getlist('selected_seats')
        total_price = float(request.POST.get('total_price', 0))
        seat_string = ",".join(seat_numbers)

        booking = Booking.objects.create(
            user=request.user,
            vehicle_type='flight',
            vehicle_id=flight.id,
            seat_number=seat_string,
            total_price=total_price,
            status='paid'
        )

        return redirect('booking_success', booking_id=booking.id)

    context = {
        'flight': flight,
    }
    return render(request, 'SelectFlightSeat.html', context)

def passengerinfo(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id)

    return render(request, 'info.html', {
        'booking': booking,
        'vehicle_type': booking.vehicle_type,
        'seat_numbers': booking.seat_numbers.split(','),
        'total_price': booking.total_price,
    })

def payment(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id)

    total_price = calculate_total_price(booking)
    booking.total_price = total_price
    booking.save()

    payment, created = Payment.objects.get_or_create(
        booking=booking,
        defaults={"status": "pending"}
    )

    client = razorpay.Client(auth=(settings.RAZORPAY_API_KEY, settings.RAZORPAY_API_SECRET))
    amount = int(total_price * 100)

    payment_order = client.order.create({"amount": amount, "currency": "INR", "payment_capture": 1})
    payment.razorpay_order_id = payment_order['id']
    payment.save()

    context = {
        "booking": booking,
        "amount": total_price,
        "payment_order_id": payment.razorpay_order_id,
        "razorpay_key": settings.RAZORPAY_API_KEY,
    }
    return render(request, 'paymentOption.html', context)

#def booking_success(request, booking_id):
    if request.method == "POST":
        razorpay_order_id = request.POST.get("razorpay_order_id")
        razorpay_payment_id = request.POST.get("razorpay_payment_id")
        razorpay_signature = request.POST.get("razorpay_signature")

        print(f"Order ID: {razorpay_order_id}")
        print(f"Payment ID: {razorpay_payment_id}")
        print(f"Signature: {razorpay_signature}")

        payment = get_object_or_404(Payment, razorpay_order_id=razorpay_order_id)

        client = razorpay.Client(auth=(settings.RAZORPAY_API_KEY, settings.RAZORPAY_API_SECRET))
        params_dict = {
            "razorpay_order_id": razorpay_order_id,
            "razorpay_payment_id": razorpay_payment_id,
            "razorpay_signature": razorpay_signature,
        }

        try:
            # Verify the payment signature
            client.utility.verify_payment_signature(params_dict)

            # Update payment status to success
            payment.razorpay_payment_id = razorpay_payment_id
            payment.razorpay_signature = razorpay_signature
            payment.status = "success"
            payment.booking.status = "paid"
            payment.save()
            payment.booking.save()

            return JsonResponse({"status": "success"})
        except SignatureVerificationError as e:
            # If signature verification fails, mark payment as failed
            print(f"Signature Verification Error: {e}")
            payment.status = "failed"
            payment.save()
            return JsonResponse({"status": "failed"})

def booking_success(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id)
    travel_object = booking.get_travel_object()
    passenger_name = request.user.username  # or booking.user.username

    if not travel_object:
        return JsonResponse({'error': 'Invalid travel object'}, status=400)

    message = f"Hello {passenger_name}, your {booking.vehicle_type.title()} ticket from {travel_object.source} to {travel_object.destination} on {travel_object.travel_date} is confirmed. Seat: {booking.seat_numbers}. Thank you for booking with NaviBook!"

    context = {
        'booking': booking,
        'travel_object': travel_object,
        'message': message,
    }
    return render(request, 'ticket_success.html', context)


def calculate_total_price(booking):
    if booking.vehicle_type == 'bus':
        vehicle = get_object_or_404(Bus, id=booking.vehicle_id)
    elif booking.vehicle_type == 'train':
        vehicle = get_object_or_404(Train, id=booking.vehicle_id)
    elif booking.vehicle_type == 'flight':
        vehicle = get_object_or_404(Flight, id=booking.vehicle_id)
    else:
        raise ValueError("Invalid vehicle type")

    price_per_seat = vehicle.price
    seat_count = len(booking.seat_numbers.split(','))
    total_price = price_per_seat * seat_count

    return total_price


def search_place(request):
    cities = City.objects.all()
    selected_city = request.GET.get('city')

    attractions = []
    if selected_city:
        attractions = Attraction.objects.filter(city__name=selected_city)

    return render(request, 'SearchPlace.html', {
        'cities': cities,
        'attractions': attractions,
        'selected_city': selected_city
    })



def driver_info(request, bus_id):
    bus = get_object_or_404(Bus, id=bus_id)
    drivers = bus.drivers.all()
    return render(request, 'driver-info.html', {'bus': bus, 'drivers': drivers})

def train_crew_info(request, train_id):
    train = get_object_or_404(Train, id=train_id)
    crew = train.crew.all()
    return render(request, 'train-crew-info.html', {'train': train, 'crew': crew})

def flight_crew_info(request, flight_id):
    flight = get_object_or_404(Flight, id=flight_id)
    crew = flight.crew.all()
    return render(request, 'flight-crew-info.html', {'flight': flight, 'crew': crew})