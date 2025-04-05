from django.db import models
from django.db.models import PROTECT

class Device(models.Model):
    ACTIVE = 'active'
    INACTIVE = 'inactive'
    
    STATUS_CHOICES = [
        (ACTIVE, 'Active'),
        (INACTIVE, 'Inactive'),
    ]

    id = models.CharField(primary_key=True, unique=True)

    name = models.CharField(max_length=100)
    status = models.CharField(
        max_length=8,
        choices=STATUS_CHOICES,
        default=INACTIVE,  # Default to 'Inactive'
    )
    longditude = models.FloatField(default=103.817027)  # Fixed typo: "longditude" -> "longitude"
    latitude = models.FloatField(default=1.390881)

    def __str__(self):
        # Returns the name in the admin panel view 
        return self.name


class DataLog(models.Model): 
    AUDIO = 'audio'  # Define the value for 'audio'

    SENSOR_TYPES = [
        (AUDIO, 'audio'),
    ]

    timestamp = models.DateTimeField(auto_now=True)  
    data = models.CharField(max_length=255, null=True)  
    metadata = models.CharField(max_length=255, null=True) 
    sensorType = models.CharField(
        max_length=50, 
        choices=SENSOR_TYPES,
        default=AUDIO, 
    )
    device = models.ForeignKey(Device, on_delete=PROTECT)


    class Meta:
        verbose_name = "Data Log"
        verbose_name_plural = "Data Logs"

    def __str__(self):
        return f"DataLog for {self.device.name} at {self.timestamp}"
