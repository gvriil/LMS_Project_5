from rest_framework import status
from rest_framework.test import APITestCase, APIClient
from django.contrib.auth import get_user_model
from django.urls import reverse

User = get_user_model()

class UsersViewsTestCase(APITestCase):
    def setUp(self):
        """Настройка тестового окружения."""
        self.client = APIClient()
        self.user_data = {
            'email': 'testuser@example.com',
            'password': 'Test1234!',
            'first_name': 'Test',
            'last_name': 'User'
        }
        self.user = User.objects.create_user(**self.user_data)

    def test_user_registration(self):
        """Тест регистрации пользователя."""
        url = '/api/users/register/'  # проверьте, что этот URL настроен
        data = {
            'email': 'newuser@example.com',
            'password': 'New1234!',
            'first_name': 'New',
            'last_name': 'User',
            'phone': '+79991234567'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_user_profile_view(self):
        """Тест просмотра профиля пользователя."""
        self.client.force_authenticate(user=self.user)
        url = f'/api/users/profile/{self.user.id}/'  # включите ID пользователя
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_user_update_view(self):
        """Тест обновления данных пользователя."""
        self.client.force_authenticate(user=self.user)
        url = f'/api/users/profile/{self.user.id}/'
        data = {'phone': '+79991234567'}
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)