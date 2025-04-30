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
            # Parse and validate input
            try:
                data = json.loads(request.body)
                route = data.get('route', [])
            except json.JSONDecodeError:
                return JsonResponse({
                    'status': 'error',
                    'message': 'Invalid JSON payload'
                }, status=400)
            
            if not isinstance(route, list):
                return JsonResponse({
                    'status': 'error',
                    'message': 'Route must be an array'
                }, status=400)
            
            # Validate coordinates
            validated_route = []
            for i, point in enumerate(route):
                if not isinstance(point, dict):
                    continue
                
                try:
                    lat = float(point.get('lat', 0))
                    lon = float(point.get('lon', 0))
                    
                    # Basic Singapore bounds check
                    if not (1.2 <= lat <= 1.5) or not (103.5 <= lon <= 104.0):
                        logger.warning(f"Point {i} outside Singapore bounds: {lat},{lon}")
                        continue
                        
                    validated_route.append({'lat': lat, 'lon': lon})
                except (TypeError, ValueError) as e:
                    logger.warning(f"Invalid coordinate at point {i}: {point}")
                    continue
            
            if not validated_route:
                return JsonResponse({
                    'status': 'error',
                    'message': 'No valid coordinates within Singapore bounds'
                }, status=400)
            
            # Run prediction pipeline
            predictions = run_flood_risk_pipeline(validated_route)
            
            # Prepare response
            successful = [p for p in predictions if p.get('risk') is not None]
            failed = [p for p in predictions if p.get('risk') is None]
            
            response_data = {
                'status': 'success',
                'predictions': successful,
                'metadata': {
                    'total_points': len(validated_route),
                    'successful_predictions': len(successful),
                    'failed_predictions': len(failed),
                    'dem_available': any(p.get('dem_available') for p in predictions),
                    'coordinate_system': 'WGS84 (lat/lon)',
                    'model_version': '1.0'
                }
            }
            
            if failed:
                response_data['errors'] = [{
                    'lat': p['lat'],
                    'lon': p['lon'],
                    'message': p.get('error', 'Unknown error')
                } for p in failed]
            
            return JsonResponse(response_data)
            
        except Exception as e:
            logger.exception("Server error during prediction")
            return JsonResponse({
                'status': 'error',
                'message': 'Internal server error',
                'detail': str(e)
            }, status=500)
    
    return JsonResponse({
        'status': 'error',
        'message': 'Only POST requests are allowed'
    }, status=405)