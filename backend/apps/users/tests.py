from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken
import json

User = get_user_model()

class UserAuthTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123"
        )
        self.refresh = RefreshToken.for_user(self.user)
        self.access_token = str(self.refresh.access_token)
        self.refresh_token = str(self.refresh)

    # ✅ GET ME
    def test_get_me_authenticated(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.access_token}")
        response = self.client.get("/api/users/me")
        data = json.loads(response.content)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(data["success"])
        self.assertEqual(data["data"]["email"], "test@example.com")

    def test_get_me_unauthenticated(self):
        response = self.client.get("/api/users/me")
        self.assertEqual(response.status_code, 401)

    # ✅ UPDATE ME
    def test_update_me(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.access_token}")
        response = self.client.patch("/api/users/me", {"name": "Rose", "bio": "Hello!"}, format="json")
        data = json.loads(response.content)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(data["success"])
        self.assertEqual(data["data"]["name"], "Rose")
        self.assertEqual(data["data"]["bio"], "Hello!")

    # ✅ LOGOUT
    def test_logout_success(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.access_token}")
        response = self.client.post("/api/users/logout", {"refresh": self.refresh_token}, format="json")
        data = json.loads(response.content)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(data["success"])

    def test_logout_invalid_token(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.access_token}")
        response = self.client.post("/api/users/logout", {"refresh": "invalidtoken"}, format="json")
        data = json.loads(response.content)
        self.assertEqual(response.status_code, 400)
        self.assertFalse(data["success"])

    # ✅ TOKEN REFRESH
    def test_token_refresh(self):
        response = self.client.post("/api/token/refresh/", {"refresh": self.refresh_token}, format="json")
        data = json.loads(response.content)
        self.assertEqual(response.status_code, 200)
        self.assertIn("access", data)

    def test_login_remember_me_accepts_email(self):
        response = self.client.post(
            "/api/users/login/remember-me",
            {
                "email": "test@example.com",
                "password": "testpass123",
                "remember_me": True,
            },
            format="json",
        )
        data = json.loads(response.content)

        self.assertEqual(response.status_code, 200)
        self.assertTrue(data["success"])
        self.assertEqual(data["data"]["user"]["email"], "test@example.com")

    def test_login_remember_me_invalid_credentials_returns_401(self):
        response = self.client.post(
            "/api/users/login/remember-me",
            {
                "email": "test@example.com",
                "password": "wrong-password",
                "remember_me": False,
            },
            format="json",
        )
        data = json.loads(response.content)

        self.assertEqual(response.status_code, 401)
        self.assertFalse(data["success"])
