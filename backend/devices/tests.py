from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from model_bakery import baker
from .models import Device, DataLog
import time

class TestDevicesModel(APITestCase):
    def setUp(self):
        # Create test device with specific attributes
        self.device = baker.make('devices.Device', 
            name='Test Device',
            status='active',
            latitude=1.3521,
            longditude=103.8198
        )
        
        # Create multiple devices with random attributes
        self.devices = baker.make('devices.Device', _quantity=1000)
        
        # Create test data logs associated with device
        self.data_logs = baker.make(
            'devices.DataLog',
            device=self.device,
            sensorType='audio',
            _quantity=100
        )

    def test_device_creation(self):
        """Test that devices are created correctly"""
        self.assertEqual(Device.objects.count(), 1001)  # 1 specific + 1000 random devices
        self.assertEqual(self.device.name, 'Test Device')
        self.assertEqual(self.device.status, 'active')

    def test_data_log_creation(self):
        """Test that data logs are created and associated with device"""
        device_logs = DataLog.objects.filter(device=self.device)
        self.assertEqual(device_logs.count(), 100)
        self.assertEqual(device_logs.first().sensorType, 'audio')

    def test_get_devices(self):
        """Test that devices can be fetched"""
        url = reverse('getall')
        start_time = time.time()
        response = self.client.get(url)
        end_time = time.time()

        execution_time = end_time - start_time
        print(f"\nAPI response time for {Device.objects.count()} devices: {execution_time:.3f} seconds")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['features']), 1001)