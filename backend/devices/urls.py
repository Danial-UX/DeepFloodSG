from django.urls import path
from .views import get_devices, upload_data

urlpatterns = [
    path('getall/', get_devices, name="getall"),
    path("upload/", upload_data, name="upload"),
]
