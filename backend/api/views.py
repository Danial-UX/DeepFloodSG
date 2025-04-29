from rest_framework.views import APIView
from rest_framework.response import Response
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from ml_model.predict import predict_flood_risk
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
def predict_flood_probability(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            route = data.get('route', [])
            
            if not isinstance(route, list):
                return JsonResponse({'error': 'Route must be an array'}, status=400)
            
            # Ensure each point has lat/lon
            validated_route = []
            for point in route:
                if not isinstance(point, dict):
                    continue
                if 'lat' not in point or 'lon' not in point:
                    continue
                try:
                    validated_route.append({
                        'lat': float(point['lat']),
                        'lon': float(point['lon'])
                    })
                except (TypeError, ValueError):
                    continue
            
            if not validated_route:
                return JsonResponse({'error': 'No valid coordinates provided'}, status=400)
            
            predictions = run_flood_risk_pipeline(validated_route)
            
            # Filter out failed predictions
            successful_predictions = [p for p in predictions if p.get('risk') is not None]
            
            return JsonResponse({
                'status': 'success',
                'predictions': successful_predictions,
                'errors': len(predictions) - len(successful_predictions)
            })
            
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': str(e)
            }, status=400)
    
    return JsonResponse({'error': 'Invalid request method'}, status=405)