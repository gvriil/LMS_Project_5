from rest_framework import generics
from .models import Lesson
from .serializers import LessonSerializer
from rest_framework import viewsets
from .models import Course
from .serializers import CourseSerializer



class LessonCreateView(generics.CreateAPIView):
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer

class LessonDetailView(generics.RetrieveAPIView):
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer

class LessonUpdateView(generics.UpdateAPIView):
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer

class LessonDeleteView(generics.DestroyAPIView):
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer


class CourseViewSet(viewsets.ModelViewSet):
    """
    ViewSet для полного CRUD функционала с курсами
    """
    queryset = Course.objects.all()
    serializer_class = CourseSerializer

