from rest_framework import serializers, status
from .models import Course, Lesson, CourseSubscription
from .validators import validate_youtube_url


class LessonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lesson
        fields = '__all__'

    # noinspection PyMethodMayBeStatic
    def validate_video_url(self, value):
        return validate_youtube_url(value)


class CourseSerializer(serializers.ModelSerializer):
    lessons_count = serializers.SerializerMethodField()
    lessons = LessonSerializer(many=True, read_only=True)
    is_owner = serializers.SerializerMethodField()
    is_subscribed = serializers.SerializerMethodField()


    class Meta:
        model = Course
        fields = ['id', 'title', 'preview', 'description', 'lessons_count', 'lessons', 'rating', 'is_subscribed', 'is_owner']
        read_only_fields = ['owner']

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        if request and hasattr(request, 'user') and request.user.is_authenticated:
            return obj.subscriptions.filter(user=request.user).exists()
        return False

    # noinspection PyMethodMayBeStatic
    def get_lessons_count(self, obj):
        return obj.lessons.count()

    def get_is_owner(self, obj):
        return obj.owner == self.context['request'].user


def test_course_serializer_data(self):
    self.client.force_authenticate(user=self.user)
    # Создаем подписку
    CourseSubscription.objects.create(user=self.user, course=self.course)
    url = f'/api/courses/{self.course.id}/'
    response = self.client.get(url)
    self.assertEqual(response.status_code, status.HTTP_200_OK)
    self.assertTrue(response.data['is_subscribed'])
    self.assertEqual(response.data['lessons_count'], 1)

from rest_framework import serializers
from .models import Payment

class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = '__all__'