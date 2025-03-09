from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APITestCase, APIClient

from materials.models import Course
from materials.validators import validate_youtube_url

User = get_user_model()


class YoutubeValidatorTestCase(TestCase):
    """Тесты для валидатора YouTube URL."""

    def test_validate_youtube_url_direct(self):
        """Прямое тестирование функции валидации."""
        # Валидные URL
        valid_urls = [
            'https://youtube.com/watch?v=dQw4w9WgXcQ',
            'https://www.youtube.com/watch?v=dQw4w9WgXcQ',
            'http://youtu.be/dQw4w9WgXcQ',
            'youtu.be/dQw4w9WgXcQ'
        ]

        for url in valid_urls:
            try:
                validate_youtube_url(url)
            except ValidationError:
                self.fail(f"URL {url} должен быть валидным")

        # Невалидные URL
        invalid_urls = [
            'https://vimeo.com/12345',
            'https://www.example.com',
            'ftp://youtube.com',
            'youtube@example.com'
        ]

        for url in invalid_urls:
            with self.assertRaises(ValidationError):
                validate_youtube_url(url)


class ValidatorAPITestCase(APITestCase):
    """Тесты API для валидатора URL."""

    def setUp(self):
        """Настройка тестового окружения."""
        self.client = APIClient()
        self.user = User.objects.create_user(
            email='test@example.com',
            password='password'
        )
        self.course = Course.objects.create(
            title='Test Course',
            description='Test Description',
            owner=self.user
        )
        self.client.force_authenticate(user=self.user)

    def test_invalid_video_url(self):
        invalid_lesson_data = {
            'title': 'Test Lesson',
            'description': 'Test Description',
            'course': self.course.id,
            'video_url': 'invalid_url'  # неправильный URL
        }
        response = self.client.post('/api/lessons/', invalid_lesson_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_youtube_validator_edge_cases(self):
        """Тест граничных случаев валидатора."""
        self.client.force_authenticate(user=self.user)

        test_urls = [
            'https://vimeo.com/12345',
            'https://www.example.com',
            '',  # Пустая строка
            None  # Значение None
        ]

        for test_url in test_urls:
            url = '/api/lessons/create/'
            data = {
                'title': 'Test Validation',
                'course': self.course.id,
                'description': 'Test',
                'video_url': test_url
            }
            response = self.client.post(url, data, format='json')
            self.assertNotEqual(response.status_code, status.HTTP_201_CREATED)


