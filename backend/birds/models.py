from django.db import models
from devices.models import Device

# Create your models here.
class Birds(models.Model):
    URBAN = 'urban'
    FOREST = 'forest'
    OTHER = 'other'
    
    ENVIRONMENT_CHOICES = [
        (URBAN, 'Urban'),
        (FOREST, 'Forest'),
        (OTHER, 'Other')
    ]

    commonName = models.CharField(max_length=100)
    speciesCode = models.CharField(max_length=100, unique=True)
    environment = models.CharField(
        max_length=50,
        choices=ENVIRONMENT_CHOICES,
        default=OTHER
    )
    priority = models.BooleanField(default=False) 
    ignore = models.BooleanField(default=False) 

    class Meta:
        verbose_name = ("Birds")
        verbose_name_plural = ("Birds")

    def __str__(self):
        return self.commonName

    @classmethod
    def get_species_with_counts(cls):
        from django.db.models import Count
        return cls.objects.annotate(count=Count('birdlog')).values('commonName', 'speciesCode', 'count')    

    @classmethod
    def get_species_count_threshold(cls, threshold=1000):
        from django.db.models import Count
        return cls.objects.annotate(
            count=Count('birdlog')
        ).values('commonName', 'count').order_by('-count')
    
    
class BirdLog(models.Model):
    class Meta:
        verbose_name = ("Bird Log")
        verbose_name_plural = ("Bird Logs")
        unique_together = ['speciesCode', 'deviceId', 'timestamp']

    def __str__(self):
        return f"{self.speciesCode} - {self.timestamp}"
    
    speciesCode = models.ForeignKey(Birds, on_delete=models.PROTECT)
    deviceId = models.ForeignKey(Device, on_delete=models.PROTECT)

    filename = models.CharField(max_length=255, null=True)
    
    beginTime = models.DateTimeField()
    timeOffset = models.IntegerField()

    timestamp = models.DateTimeField()
    
    confidence = models.FloatField()

    @classmethod
    def get_location_time_counts(cls):
        from django.db.models import Count
        from django.db.models.functions import ExtractHour
        from django.db.models import Case, When, Value, CharField
        
        def get_time_of_day(hour):
            if 5 <= hour <= 11:
                return 'Morning'
            elif 17 <= hour <= 23:
                return 'Evening'
            return 'Other'
        
        return cls.objects.annotate(
            hour=ExtractHour('timestamp'),
            time_of_day=Case(
                When(hour__range=(5, 11), then=Value('Morning')),
                When(hour__range=(17, 23), then=Value('Evening')),
                default=Value('Other'),
                output_field=CharField(),
            )
        ).values('deviceId__latitude', 'time_of_day').annotate(
            count=Count('id')
        ).filter(time_of_day__in=['Morning', 'Evening'])

    @classmethod
    def get_device_time_counts(cls):
        from django.db.models import Count
        from django.db.models.functions import ExtractHour
        from django.db.models import Case, When, Value, CharField
        
        return cls.objects.annotate(
            hour=ExtractHour('timestamp'),
            time_of_day=Case(
                When(hour__range=(5, 11), then=Value('Morning')),
                When(hour__range=(17, 23), then=Value('Evening')),
                default=Value('Other'),
                output_field=CharField(),
            )
        ).values(
            'deviceId__id', 
            'deviceId__name',
            'deviceId__latitude', 
            'deviceId__longditude',
            'time_of_day'
        ).annotate(
            count=Count('id')
        ).filter(time_of_day__in=['Morning', 'Evening'])