from django.contrib import admin
from .models import Birds, BirdLog
from django import forms
import csv
from io import StringIO
from devices.models import Device
from datetime import datetime, timedelta
from django.utils.timezone import make_aware
from django.urls import path
from django.shortcuts import render, redirect
from django.conf.locale.en import formats as en_formats
from django.http import JsonResponse
import threading
import logging
import time
from django.db import connection, connections

logger = logging.getLogger(__name__)

en_formats.DATETIME_FORMAT = "d/m/y h:i:sA"

class CsvImportForm(forms.Form):
    csv_file = forms.FileField(label='CSV File')

class birdAdmin(admin.ModelAdmin):
    list_display = ('speciesCode', 'commonName', 'environment', 'priority', 'ignore')

    ordering = ['commonName']
    list_filter = ['environment', 'priority', 'ignore']
    search_fields = ['speciesCode', 'commonName']

class birdLogAdmin(admin.ModelAdmin):
    change_list_template = "admin/birds/birdlog/change_list.html"
    list_display = ('speciesCode', 'timestamp', 'confidence', 'deviceId', 'filename')

    ordering = ['timestamp']
    list_filter = ['timestamp', 'deviceId']
    search_fields = ['speciesCode__commonName']

    def get_urls(self):
        urls = super().get_urls()
        my_urls = [
            path('import-csv/', self.import_csv),
            path('task-status/<str:task_id>/', self.task_status),
        ]
        return my_urls + urls

    def process_csv_file(self, file_content, filename, task_id):
        """Process a single CSV file in a thread"""
        try:
            # Acquire semaphore before processing
            self.thread_semaphore.acquire()
            with self.thread_lock:
                self.active_threads += 1

            csvf = StringIO(file_content.decode())
            csvreader = csv.reader(csvf, delimiter='\t')
            next(csvreader)  # Skip header
            
            total_imported = 0
            duplicates = 0
            errors = []
            
            for row_num, row in enumerate(csvreader, start=2):
                try:
                    if len(row) < 12:
                        errors.append(f"Row {row_num}: Invalid number of columns")
                        continue

                    selection, view, channel, audio_begin_sec, audio_end_sec, low_freq, high_freq, common_name, species_code, confidence, filename, timeOffset = row

                    fileNameParse = filename.split('/')
                    filename = fileNameParse[-1]

                    try:
                        deviceId = filename.split('_')[0]
                        date = filename.split('_')[1]
                        fileBeginTime = filename.split('_')[2].strip('.wav')
                    except IndexError as e:
                        errors.append(f"Row {row_num}: Invalid filename format: {filename}")
                        continue

                    # Create or get device
                    try:
                        device, _ = Device.objects.get_or_create(
                            id=deviceId,
                            defaults={'name': f'Device {deviceId}', 'status': 'active'}
                        )
                    except Exception as e:
                        errors.append(f"Row {row_num}: Error creating device: {str(e)}")
                        continue

                    # Get or create bird - handle duplicate species codes
                    try:
                        # First try to get existing bird
                        bird = Birds.objects.filter(speciesCode=species_code).first()
                        if not bird:
                            # If no bird exists, create a new one
                            bird = Birds.objects.create(
                                speciesCode=species_code,
                                commonName=common_name
                            )
                    except Exception as e:
                        errors.append(f"Row {row_num}: Error handling bird: {str(e)}")
                        continue

                    try:
                        beginTime = make_aware(datetime.strptime(f"{date} {fileBeginTime}", "%Y%m%d %H%M%S"))
                        timestamp = beginTime + timedelta(seconds=int(float(audio_begin_sec)))
                    except (ValueError, TypeError) as e:
                        errors.append(f"Row {row_num}: Error parsing date/time: {str(e)}")
                        continue

                    # Try to create bird log, skip if duplicate
                    try:
                        BirdLog.objects.create(
                            speciesCode=bird,
                            deviceId=device,
                            filename=filename,
                            beginTime=beginTime,
                            timeOffset=int(float(timeOffset)),
                            timestamp=timestamp,
                            confidence=float(confidence)
                        )
                        total_imported += 1
                    except Exception as e:
                        if 'unique constraint' in str(e).lower():
                            duplicates += 1
                            continue
                        errors.append(f"Row {row_num}: Error creating bird log: {str(e)}")
                        continue
                    
                except Exception as e:
                    errors.append(f"Row {row_num}: Unexpected error: {str(e)}")
                    continue
                    
            self.task_results[task_id] = {
                'status': 'SUCCESS',
                'result': {
                    'success': True,
                    'file_imported': total_imported,
                    'file_duplicates': duplicates,
                    'file_errors': errors
                }
            }
            
        except Exception as e:
            logger.error(f"Error processing file {filename}: {str(e)}")
            self.task_results[task_id] = {
                'status': 'ERROR',
                'error': str(e)
            }
        finally:
            # Clean up resources
            try:
                csvf.close()
            except:
                pass
            
            # Close database connections
            try:
                connection.close()
                for conn in connections.all():
                    conn.close()
            except Exception as e:
                logger.error(f"Error closing database connections: {str(e)}")
            
            # Release semaphore and update active threads count
            self.thread_semaphore.release()
            with self.thread_lock:
                self.active_threads -= 1
            # Remove thread reference
            if task_id in self.task_threads:
                del self.task_threads[task_id]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.task_results = {}
        self.task_threads = {}
        self.active_threads = 0
        self.max_threads = 50  # Maximum number of concurrent threads
        self.thread_lock = threading.Lock()
        self.thread_semaphore = threading.Semaphore(self.max_threads)

    def task_status(self, request, task_id):
        try:
            if task_id in self.task_results:
                result = self.task_results[task_id]
                if result['status'] == 'SUCCESS':
                    return JsonResponse(result)
                else:
                    return JsonResponse(result, status=500)
            else:
                return JsonResponse({
                    'status': 'PENDING',
                    'message': 'Task is still processing'
                })
        except Exception as e:
            logger.error(f"Error checking task status: {str(e)}")
            return JsonResponse({
                'status': 'ERROR',
                'error': str(e)
            }, status=500)

    def import_csv(self, request):
        if request.method == "POST":
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                try:
                    # Handle AJAX request
                    files = request.FILES.getlist('csv_files')
                    if not files:
                        return JsonResponse({
                            'success': False,
                            'error': 'No files were uploaded'
                        }, status=400)

                    results = []
                    for csv_file in files:
                        try:
                            file_content = csv_file.read()
                            # Generate a unique task ID using timestamp and random number
                            task_id = f"task_{int(time.time() * 1000)}_{len(self.task_results)}"
                            
                            # Create a new thread for processing
                            thread = threading.Thread(
                                target=self.process_csv_file,
                                args=(file_content, csv_file.name, task_id)
                            )
                            thread.daemon = True  # Thread will exit when main program exits
                            thread.start()
                            
                            # Store thread reference
                            self.task_threads[task_id] = thread
                            
                            results.append({
                                'filename': csv_file.name,
                                'task_id': task_id
                            })
                        except Exception as e:
                            logger.error(f"Error processing file {csv_file.name}: {str(e)}")
                            return JsonResponse({
                                'success': False,
                                'error': f"Error processing file {csv_file.name}: {str(e)}"
                            }, status=500)
                    
                    return JsonResponse({
                        'success': True,
                        'message': 'Files are being processed',
                        'tasks': results,
                        'max_threads': self.max_threads
                    })
                except Exception as e:
                    logger.error(f"Error in import_csv view: {str(e)}")
                    return JsonResponse({
                        'success': False,
                        'error': str(e)
                    }, status=500)
            else:
                # Handle regular form submission
                form = CsvImportForm()
                payload = {"form": form}
                return render(request, "admin/birds/birdlog/csv_form.html", payload)
        
        form = CsvImportForm()
        payload = {"form": form}
        return render(request, "admin/birds/birdlog/csv_form.html", payload)

admin.site.register(Birds, birdAdmin)
admin.site.register(BirdLog, birdLogAdmin)
