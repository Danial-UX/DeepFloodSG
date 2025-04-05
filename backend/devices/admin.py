from django.contrib import admin
from .models import Device, DataLog

from django.http import HttpResponse
import datetime, csv

class ExportCsvMixin:
    def export_as_csv(self, request, queryset):
        meta = self.model._meta
        field_names = [field.name for field in meta.fields]

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename={}.csv'.format(meta)
        writer = csv.writer(response)

        writer.writerow(field_names)
        for obj in queryset:
            row = writer.writerow([getattr(obj, field) for field in field_names])

        return response

    export_as_csv.short_description = "Export Selected Fields"

class deviceAdmin(admin.ModelAdmin, ExportCsvMixin):
    actions = ["export_as_csv"]
    list_display = ('id', 'name', 'status', 'longditude', 'latitude')
    ordering = ['id']
    list_filter = ['status']
    search_fields = ['name']

class dataLogAdmin(admin.ModelAdmin, ExportCsvMixin):
    actions = ["export_as_csv"]
    list_display = ('id', 'timestamp', 'data', 'metadata', 'sensorType', 'device')
    ordering = ['timestamp']
    list_filter = ['timestamp', 'sensorType', 'device']
    search_fields = ['device']


admin.site.register(Device, deviceAdmin)
admin.site.register(DataLog, dataLogAdmin)

admin.site.site_header = 'DeepFloodSG Admin Site'
admin.site.site_title = 'DeepFloodSG Admin Site'
admin.site.index_title = 'Welcome to DeepFloodSG Admin Portal'