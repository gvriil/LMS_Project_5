from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase, APIRequestFactory, APIClient
from rest_framework import status
from materials.models import Course, Lesson, CourseSubscription
from materials.serializers import CourseSerializer, LessonSerializer

User = get_user_model()


class SerializersTestCase(APITestCase):
    """Тесты для сериализаторов."""

    def setUp(self):
        """Настройка тестового окружения."""
        self.client = APIClient()
        self.factory = APIRequestFactory()

        # Создаем пользователя
        self.user = User.objects.create_user(
            email='test@example.com',
            password='password'
        )

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
            owner=self.user,
            video_url='https://youtube.com/watch?v=dQw4w9WgXcQ'
        )

    def test_course_serializer_methods(self):
        """Тест методов класса CourseSerializer."""
        request = self.factory.get('/')
        request.user = self.user

        serializer = CourseSerializer(
            instance=self.course,
            context={'request': request}
        )

        # Проверка метода get_lessons_count
        self.assertEqual(serializer.get_lessons_count(self.course), 1)

        # Проверка метода get_is_owner
        self.assertTrue(serializer.get_is_owner(self.course))

        # Проверка get_is_subscribed для неподписанного пользователя
        self.assertFalse(serializer.get_is_subscribed(self.course))

        # Создаем подписку и проверяем снова
        CourseSubscription.objects.create(user=self.user, course=self.course)
        self.assertTrue(serializer.get_is_subscribed(self.course))

    def test_course_serializer_anonymous(self):
        """Тест сериализатора с анонимным пользователем."""
        request = self.factory.get('/')
        request.user = type('AnonymousUser', (), {'is_authenticated': False})()

        serializer = CourseSerializer(
            instance=self.course,
            context={'request': request}
        )

        # Анонимный пользователь не подписан
        self.assertFalse(serializer.get_is_subscribed(self.course))

    def test_lesson_serializer_validation(self):
        """Тест валидации в LessonSerializer."""
        serializer = LessonSerializer(data={
            'title': 'New Lesson',
            'course': self.course.id,
            'description': 'Test Description',
            'video_url': 'https://youtube.com/watch?v=test'
        })

        self.assertTrue(serializer.is_valid())

        # Проверка с невалидным URL
        serializer = LessonSerializer(data={
            'title': 'New Lesson',
            'course': self.course.id,
            'description': 'Test Description',
            'video_url': 'https://example.com/video'
        })

        self.assertFalse(serializer.is_valid())
        self.assertIn('video_url', serializer.errors)

    def test_course_serializer_data(self):
        """Тест данных в CourseSerializer при API-запросе."""
        self.client.force_authenticate(user=self.user)

        # Создаем подписку
        CourseSubscription.objects.create(user=self.user, course=self.course)

        url = f'/api/courses/{self.course.id}/'

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['is_subscribed'])
        self.assertEqual(response.data['lessons_count'], 1)