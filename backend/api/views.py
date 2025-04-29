from rest_framework.views import APIView
from rest_framework.response import Response
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.http import JsonResponse
import json
from flood_prediction.mlp_model.run_mlp_pipeline import run_flood_risk_pipeline

# Class-based View (APIView)
@method_decorator(csrf_exempt, name='dispatch')
class FloodPredictionView(APIView):
    def post(self, request, *args, **kwargs):
        location = request.data.get("location")
        rainfall = float(request.data.get("rainfall", 0))

        try:
            risk = predict_flood_risk(location, rainfall)
            return Response({"flood_risk": risk})
        except Exception as e:
            return Response({"error": str(e)}, status=400)

# Function-based View
@csrf_exempt
def predict_flood_risk(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            route = data.get('route', [])  # List of [lat, lon]
            
            predictions = run_flood_risk_pipeline(route)

            # Return list of {"lat": ..., "lon": ..., "risk": ...}
            return JsonResponse(predictions, safe=False)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    return JsonResponse({'error': 'Invalid request method'}, status=405)