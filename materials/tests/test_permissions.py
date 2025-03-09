from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from rest_framework import status
from rest_framework.test import APITestCase, APIClient

from materials.models import Course, Lesson
from materials.permissions import IsModerator, NotModerator, IsOwner, ModeratorOrOwner

User = get_user_model()


class PermissionsTestCase(APITestCase):
    """Тесты для системы разрешений."""

    def setUp(self):
        """Настройка тестового окружения."""
        self.client = APIClient()

        # Создаем пользователей
        self.user = User.objects.create_user(
            email='user@example.com',
            password='password'
        )

        # Создаем модератора
        self.moderator_group = Group.objects.create(name='moderators')
        self.moderator = User.objects.create_user(
            email='mod@example.com',
            password='password'
        )
        self.moderator.groups.add(self.moderator_group)

        # Создаем курс и урок
        self.course = Course.objects.create(
            title='Test Course',
            description='Course Description',
            owner=self.user
        )

        self.lesson = Lesson.objects.create(
            title='Test Lesson',
            course=self.course,
            description='Lesson Description',
            owner=self.user
        )

    def test_is_moderator_permission(self):
        """Тест класса IsModerator."""
        permission = IsModerator()
        request = type('Request', (), {'user': self.moderator})()

        self.assertTrue(permission.has_permission(request, None))
        self.assertTrue(permission.has_object_permission(request, None, None))

        # Проверяем не-модератора
        request = type('Request', (), {'user': self.user})()
        self.assertFalse(permission.has_permission(request, None))

    def test_not_moderator_permission(self):
        """Тест класса NotModerator."""
        permission = NotModerator()

        # Проверка для обычного пользователя
        request = type('Request', (), {'user': self.user})()
        self.assertTrue(permission.has_permission(request, None))

        # Проверка для модератора
        request = type('Request', (), {'user': self.moderator})()
        self.assertFalse(permission.has_permission(request, None))

    def test_is_owner_permission(self):
        """Тест класса IsOwner."""
        permission = IsOwner()
        request = type('Request', (), {'user': self.user})()

        # Проверка владельца
        self.assertTrue(permission.has_object_permission(request, None, self.lesson))

        # Проверка не-владельца
        other_user = User.objects.create_user(
            email='other@example.com',
            password='password'
        )
        request = type('Request', (), {'user': other_user})()
        self.assertFalse(permission.has_object_permission(request, None, self.lesson))

    def test_moderator_or_owner_permission(self):
        """Тест класса ModeratorOrOwner."""
        permission = ModeratorOrOwner()

        # Проверка модератора не-владельца
        request = type('Request', (), {'user': self.moderator})()
        self.assertTrue(permission.has_permission(request, None))
        self.assertTrue(permission.has_object_permission(request, None, self.lesson))

        # Проверка владельца не-модератора
        request = type('Request', (), {'user': self.user})()
        self.assertFalse(permission.has_permission(request, None))

    def test_lesson_access_by_nonowner(self):
        """Тест доступа не-владельца к уроку."""
        # Создаем другого пользователя
        other_user = User.objects.create_user(
            email='other@example.com',
            password='otherpass'
        )
        self.client.force_authenticate(user=other_user)
        url = f'/api/lessons/{self.lesson.id}/update/'
        data = {'title': 'Unauthorized Update'}
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_permission_edge_cases(self):
        """Тест граничных случаев разрешений."""
        new_moderator = User.objects.create_user(
            email='mod2@example.com',
            password='password'
        )
        new_moderator.groups.add(self.moderator_group)
        self.client.force_authenticate(user=new_moderator)

        # Попытка удалить чужой урок
        url = f'/api/lessons/{self.lesson.id}/delete/'
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
