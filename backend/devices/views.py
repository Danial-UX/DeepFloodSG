from rest_framework.response import Response
from rest_framework.decorators import api_view
from .models import Device
import json
from django.http import JsonResponse
from asgiref.sync import async_to_sync
from .data_processor import add_to_queue  # Ensure correct import
from django.db.models import F, Value, CharField
from django.db.models.functions import JSONObject, Concat
from django.core.serializers.json import DjangoJSONEncoder
from django.db.models.aggregates import Aggregate
from django.db.models.expressions import RawSQL

class JSONBuildObject(Aggregate):
    function = 'JSONB_BUILD_OBJECT'
    template = "%(function)s(%(expressions)s)"
    allow_distinct = True

def get_devices_as_geojson_efficient():
    # Use database-level JSON construction for better performance
    features = Device.objects.annotate(
        feature=JSONObject(
            type=Value('Feature'),
            id=F('id'),
            geometry=JSONObject(
                type=Value('Point'),
                coordinates=RawSQL("ARRAY[longditude, latitude]", [])
            ),
            properties=JSONObject(
                name=F('name'),
                id=F('id'),
                status=F('status'),
            )
        )
    ).values_list('feature', flat=True)
    
    # Construct the final GeoJSON
    geojson = {
        "type": "FeatureCollection",
        "features": list(features)
    }
    
    return geojson


@api_view(['GET'])
def get_devices(request):
    """Fetch all devices"""
    # devices = Device.objects.all()
    # serializer = DeviceSerializer(devices, many=True)
    return Response(get_devices_as_geojson_efficient(), status=200)


# @api_view(['GET'])
# def get_devices(request):
#     """Fetch all devices"""
#     devices = Device.objects.all()
#     serializer = GeoDeviceSerializer(devices, many=True)
#     return Response(serializer.data, status=200)

@api_view(['POST'])
def upload_data(request):
    """Sync API view for devices to upload data"""
    if request.method == "POST":
        try:
            data = json.loads(request.body)  # Parse JSON
            async_to_sync(add_to_queue)(data)  # Convert async function to sync
            return JsonResponse({"message": "Data received"})
        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON"}, status=400)
    return JsonResponse({"error": "Invalid request method"}, status=405)
