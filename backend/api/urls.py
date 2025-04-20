from django.urls import path
from .views import FloodPredictionView

urlpatterns = [
    path("predict-flood/", FloodPredictionView.as_view()), 
]
