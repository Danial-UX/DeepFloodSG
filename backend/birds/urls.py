# urls.py
from django.urls import path
from .views import get_species_data
from .views import get_species_count
from .views import get_birds_by_device

urlpatterns = [
    path('species-data/', get_species_data, name='species_data'),
    path('species-count/', get_species_count, name='species_count'),
    path('birds-by-device/', get_birds_by_device, name='get_birds_by_device'),
]