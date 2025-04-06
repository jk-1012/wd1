from .models import Bus, Train, Flight
from django.utils import timezone

def get_vehicle_object(vehicle_type, vehicle_id):
    """
    Returns the specific travel object (BusDetail, TrainDetail, FlightDetail) based on type and ID.
    """
    if vehicle_type == 'bus':
        return Bus.objects.filter(id=vehicle_id).first()
    elif vehicle_type == 'train':
        return Train.objects.filter(id=vehicle_id).first()
    elif vehicle_type == 'flight':
        return Flight.objects.filter(id=vehicle_id).first()
    return None

def get_formatted_datetime():
    return timezone.now().strftime("%Y-%m-%d %H:%M:%S")
