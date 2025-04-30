from django.urls import path
from . import views

urlpatterns = [
    path("predict-flood/", views.FloodPredictionView.as_view(), name="predict_flood"), 
    path('predict_flood_risk/', views.predict_flood_probability, name='predict_flood_probability'),
]