from django.core.exceptions import ValidationError
import re

from rest_framework import status


def validate_youtube_url(value):
    """
    Проверяет, что URL ссылается только на youtube.com.
    """
    if value:
        youtube_pattern = r'(?:https?:\/\/)?(?:www\.)?(?:youtube\.com|youtu\.be)\/'
        if not re.match(youtube_pattern, value):
            raise ValidationError(
                'Разрешены только ссылки на youtube.com'
            )
    return value


def test_invalid_video_url(self):
    self.client.force_authenticate(user=self.user)
    url = '/api/lessons/create/'
    data = {
        'title': 'Invalid Video',
        'course': self.course.id,
        'description': 'Test',
        'video_url': 'https://invalid-url.com/video'
    }
    response = self.client.post(url, data, format='json')
    self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


def test_youtube_validator_edge_cases(self):
    # Проверка граничных случаев валидатора
    self.client.force_authenticate(user=self.user)

    # Проверка невалидных URL-адресов
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