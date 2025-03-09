from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase

from users.serializers import UserSerializer, UserCreateSerializer

User = get_user_model()


class UserSerializersTestCase(APITestCase):
    """Тесты для сериализаторов пользователей."""

    def setUp(self):
        """Настройка тестового окружения."""
        self.user_data = {
            'email': 'test@example.com',
            'password': 'securepass123',
            'phone': '+79001234567'
        }
        self.user = User.objects.create_user(
            email=self.user_data['email'],
            password=self.user_data['password'],
            phone=self.user_data['phone']
        )

    def test_user_serializer(self):
        """Тест сериализации пользователя."""
        serializer = UserSerializer(instance=self.user)
        data = serializer.data

        self.assertEqual(data['email'], self.user_data['email'])
        self.assertEqual(data['phone'], self.user_data['phone'])
        self.assertNotIn('password', data)

    def test_user_create_serializer(self):
        """Тест создания пользователя через сериализатор."""
        new_user_data = {
            'email': 'new@example.com',
            'password': 'newpass123',
            'phone': '+79009876543'
        }

        serializer = UserCreateSerializer(data=new_user_data)
        self.assertTrue(serializer.is_valid())

        user = serializer.save()
        self.assertEqual(user.email, new_user_data['email'])
        self.assertEqual(user.phone, new_user_data['phone'])
        self.assertTrue(user.check_password(new_user_data['password']))
