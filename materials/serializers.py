from rest_framework import serializers
from .models import Course, Lesson
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
        fields = ['id', 'title', 'preview', 'description', 'lessons_count', 'lessons', 'rating', 'is_subscribed']
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
