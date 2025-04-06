from django.contrib import admin
from .models import User, Bus, Train, Flight, SeatAvailability, Booking, PassengerDetail, Payment ,City, Attraction

admin.site.register(User)
admin.site.register(Bus)
admin.site.register(Train)
admin.site.register(Flight)
admin.site.register(SeatAvailability)
admin.site.register(Booking)
admin.site.register(PassengerDetail)
admin.site.register(Payment)
admin.site.register(City)
admin.site.register(Attraction)
