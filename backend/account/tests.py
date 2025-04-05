from django.test import TestCase

from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status

User = get_user_model()

class AuthTestCase(APITestCase):
    def setUp(self):
        """Create a test user for authentication tests"""
        self.user = User.objects.create_user(username="testuser", password="testpassword")
        self.login_url = reverse("login")  # Ensure "login" is the name of the login URL
        self.register_url = reverse("register")  # Ensure "register" is the name of the register URL

    def test_register_user(self):
        """Test user registration endpoint"""
        data = {
            "username": "newuser",
            "password": "newpassword",
            "email": "newuser@example.com"
        }
        response = self.client.post(self.register_url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(User.objects.filter(username="newuser").exists())

    def test_register_user_with_existing_username(self):
        """Ensure registration fails if username already exists"""
        data = {
            "username": "testuser",  # Already exists in setUp()
            "password": "anotherpassword",
            "email": "duplicate@example.com"
        }
        response = self.client.post(self.register_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_login_with_valid_credentials(self):
        """Ensure login works with correct credentials"""
        data = {
            "username": "testuser",
            "password": "testpassword"
        }
        response = self.client.post(self.login_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("token", response.data)  # Assuming you return a token in response

    def test_login_with_invalid_credentials(self):
        """Ensure login fails with incorrect password"""
        data = {
            "username": "testuser",
            "password": "wrongpassword"
        }
        response = self.client.post(self.login_url, data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

