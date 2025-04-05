import os
from django.http import JsonResponse
import pandas as pd
from .models import Birds, BirdLog
from django.db.models import Case, When, Value, CharField


def get_species_data(request):
    species_data = Birds.get_species_with_counts()
    return JsonResponse(list(species_data), safe=False)

def get_species_count(request):
    threshold = 10 # currently only 3 since small dataset
    species_counts = Birds.get_species_count_threshold(threshold)

    
    above_threshold = []
    below_threshold_count = 0
    below_threshold_species = 0
    
    for species in species_counts:
        if species['count'] > threshold:
            above_threshold.append(species)
            
        else:
            below_threshold_count += species['count']
            below_threshold_species += 1
    
    if below_threshold_species > 0:
        above_threshold.append({
            'commonName': f'Others ({below_threshold_species} species)',
            'count': below_threshold_count
        })

    # print(above_threshold)
    
    return JsonResponse(above_threshold, safe=False)

def get_birds_by_device(request):
    device_counts = BirdLog.get_device_time_counts()
    
    devices = {}
    for entry in device_counts:
        device_id = entry['deviceId__id']
        if device_id not in devices:
            devices[device_id] = {
                'deviceId': device_id,
                'name': entry['deviceId__name'],
                'latitude': entry['deviceId__latitude'],
                'longitude': entry['deviceId__longditude'],
                'Morning': 0,
                'Evening': 0
            }
        devices[device_id][entry['time_of_day']] = entry['count']
    
    # sort by name without the last character (m)
    result = sorted(devices.values(), key=lambda x: x['name'][:-1])
    return JsonResponse(result, safe=False)