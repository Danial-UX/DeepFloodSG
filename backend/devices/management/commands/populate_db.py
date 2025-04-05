from django.core.management.base import BaseCommand
from model_bakery import baker
from devices.models import Device, DataLog
from birds.models import Birds
import random
from django.utils import timezone
from datetime import timedelta

class Command(BaseCommand):
    help = 'Populate database with sample devices and data logs'

    def add_arguments(self, parser):
        parser.add_argument('--devices', type=int, default=40, help='Number of devices to create')
        parser.add_argument('--logs', type=int, default=12, help='Number of logs per device')

    def handle(self, *args, **options):
        confirm = input('Generate devices, log, and birds from preset? (yes/random/no): ')
        num_devices = options['devices']
        logs_per_device = options['logs']

        if confirm == 'random':
            # Singapore bounds
            LAT_BOUNDS = (1.344, 1.422)  # Singapore latitude range
            LONG_BOUNDS = (103.76, 103.83)  # Singapore longitude range

            self.stdout.write('Creating devices...')
            
            # Create devices with realistic Singapore coordinates
            devices = []
            for i in range(num_devices):
                device = baker.make(
                    'devices.Device',
                    name=f'Device-SG{i+1:03d}',
                    status=random.choice(['active', 'inactive']),
                    latitude=random.uniform(*LAT_BOUNDS),
                    longditude=random.uniform(*LONG_BOUNDS)
                )
                devices.append(device)
                self.stdout.write(f'Created device: {device.name}')

            self.stdout.write('Creating data logs...')
            
            # Create data logs for each device
            for device in devices:
                # Create logs with timestamps spread over the last 30 days
                for _ in range(logs_per_device):
                    days_ago = random.randint(0, 30)
                    hours_ago = random.randint(0, 23)
                    timestamp = timezone.now() - timedelta(days=days_ago, hours=hours_ago)
                    
                    baker.make(
                        'devices.DataLog',
                        device=device,
                        sensorType=random.choice(['audio', 'temperature', 'humidity']),
                        timestamp=timestamp,
                        data={'value': random.uniform(20, 30)},
                        metadata={'location': 'Singapore', 'device_type': 'sensor'}
                    )

            self.stdout.write(self.style.SUCCESS(
                f'Successfully created {num_devices} devices with {logs_per_device} logs each'
            ))
        elif confirm == 'yes':

            # Create devices with preset coordinates
            devices = [
                {
                    "id": "2MA05544",
                    "name": "0m",
                    "latitude": 1.391114,
                    "longitude": 103.817298,
                    "status": "active"
                },
                {
                    "id": "SMA02860",
                    "name": "12.5m",
                    "latitude": 1.391114,
                    "longitude": 103.817187,
                    "status": "active"
                },
                {
                    "id": "2MA05557",
                    "name": "25m",
                    "latitude": 1.391114,
                    "longitude": 103.817076,
                    "status": "active"
                },
                {
                    "id": "SMA02924",
                    "name": "37.5m",
                    "latitude": 1.391114,
                    "longitude": 103.816965,
                    "status": "active"
                },
                {
                    "id": "2MA05521",
                    "name": "50m",
                    "latitude": 1.391114,
                    "longitude": 103.816854,
                    "status": "active"
                },
                {
                    "id": "2MA05846",
                    "name": "100m",
                    "latitude": 1.391114,
                    "longitude": 103.816301,
                    "status": "active"
                },
                {
                    "id": "2MA05518",
                    "name": "275m",
                    "latitude": 1.391114,
                    "longitude": 103.814324,
                    "status": "active"
                },
                {
                    "id": "2MA05513",
                    "name": "450m",
                    "latitude": 1.391114,
                    "longitude": 103.812348,
                    "status": "active"
                },
                {
                    "id": "2MA05583",
                    "name": "625m",
                    "latitude": 1.391114,
                    "longitude": 103.810371,
                    "status": "active"
                },
                {
                    "id": "2MA05851",
                    "name": "800m",
                    "latitude": 1.391114,
                    "longitude": 103.808394,
                    "status": "active"
                }
            ]

            # create birds
            birds = [
                {
                    "commonName": "Crimson Sunbird",
                    "speciesCode": "eacsun1",
                    "environment": "Urban",
                    "priority": True,
                    "ignore": False
                },
                {
                    "commonName": "Brown-throated Sunbird",
                    "speciesCode": "pltsun2",
                    "environment": "Urban",
                    "priority": True,
                    "ignore": False
                },
                {
                    "commonName": "Asian Fairy-bluebird",
                    "speciesCode": "asfblu1",
                    "environment": "Forest",
                    "priority": True,
                    "ignore": False
                },
                {
                    "commonName": "Banded Woodpecker",
                    "speciesCode": "banwoo2",
                    "environment": "Forest",
                    "priority": True,
                    "ignore": False
                },
                {
                    "commonName": "Common Hill Myna",
                    "speciesCode": "hilmyn",
                    "environment": "Forest",
                    "priority": True,
                    "ignore": False
                },
                {
                    "commonName": "Brown Boobook",
                    "speciesCode": "brnhao1",
                    "environment": "Forest",
                    "priority": True,
                    "ignore": False
                },
                {
                    "commonName": "Short-tailed Babbler",
                    "speciesCode": "shtbab1",
                    "environment": "Forest",
                    "priority": True,
                    "ignore": False
                },
                {
                    "commonName": "Pin-striped Tit-Babbler",
                    "speciesCode": "sttbab1",
                    "environment": "Forest",
                    "priority": True,
                    "ignore": False
                },
                {
                    "commonName": "Yellow-vented Bulbul",
                    "speciesCode": "yevbul1",
                    "environment": "Urban",
                    "priority": True,
                    "ignore": False
                },
                {
                    "commonName": "Olive-winged Bulbul",
                    "speciesCode": "olwbul1",
                    "environment": "Urban",
                    "priority": True,
                    "ignore": False
                },
                {
                    "commonName": "Blue-throated Bee-eater",
                    "speciesCode": "btbeat2",
                    "environment": "Urban",
                    "priority": True,
                    "ignore": False
                },
                {
                    "commonName": "Blue-winged Leafbird",
                    "speciesCode": "blwlea1",
                    "environment": "Urban",
                    "priority": True,
                    "ignore": False
                },
                {
                    "commonName": "Arctic Warbler",
                    "speciesCode": "arcwar1",
                    "environment": "Urban",
                    "priority": True,
                    "ignore": False
                },
                {
                    "commonName": "Scarlet-backed Flowerpecker",
                    "speciesCode": "scbflo1",
                    "environment": "Urban",
                    "priority": True,
                    "ignore": False
                },
                {
                    "commonName": "Orange-bellied Flowerpecker",
                    "speciesCode": "orbflo1",
                    "environment": "Forest",
                    "priority": True,
                    "ignore": False
                },
                {
                    "commonName": "Red-crowned Barbet",
                    "speciesCode": "recbar1",
                    "environment": "Forest",
                    "priority": True,
                    "ignore": False
                },
                {
                    "commonName": "Changeable Hawk-Eagle",
                    "speciesCode": "y00839",
                    "environment": "Forest",
                    "priority": True,
                    "ignore": False
                },
                {
                    "commonName": "Greater Racket-tailed Drongo",
                    "speciesCode": "grtdro1",
                    "environment": "Forest",
                    "priority": True,
                    "ignore": False
                },
                {
                    "commonName": "Long-tailed Parakeet",
                    "speciesCode": "lotpar2",
                    "environment": "Urban",
                    "priority": True,
                    "ignore": False
                },
                {
                    "commonName": "Common Flameback",
                    "speciesCode": "comfla1",
                    "environment": "Urban",
                    "priority": True,
                    "ignore": False
                },
                {
                    "commonName": "Olive-backed Sunbird",
                    "speciesCode": "olbsun4",
                    "environment": "Urban",
                    "priority": True,
                    "ignore": False
                },
                {
                    "commonName": "Oriental Bay-Owl",
                    "speciesCode": "orbowl1",
                    "environment": "Other",
                    "priority": False,
                    "ignore": True
                },
                {
                    "commonName": "Sunda Scops-Owl",
                    "speciesCode": "susowl2",
                    "environment": "Other",
                    "priority": False,
                    "ignore": True
                },
                {
                    "commonName": "Black-naped Oriole",
                    "speciesCode": "blnori1",
                    "environment": "Other",
                    "priority": False,
                    "ignore": True
                }
                ]

            for device in devices:
                baker.make(
                    'devices.Device',
                    id=device['id'],
                    name=device['name'],
                    latitude=device['latitude'],
                    longditude=device['longitude'],
                    status=device['status']
                )

            for bird in birds:
                baker.make(
                    'birds.Birds',
                    commonName=bird['commonName'],
                    speciesCode=bird['speciesCode'],
                    environment=bird['environment'],
                    priority=bird['priority'],
                    ignore=bird['ignore']
                )

            self.stdout.write(self.style.SUCCESS(
                f'Successfully created {len(devices)} devices and {len(birds)} birds'
            ))


        else:
            self.stdout.write(self.style.WARNING('No options selected'))
