from rest_framework.views import APIView
from rest_framework.response import Response
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from ml_model.predict import predict_flood_risk

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
