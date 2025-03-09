from django.shortcuts import get_object_or_404
from rest_framework import generics, viewsets
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Course, CourseSubscription
from .models import Lesson
from .paginators import MaterialsPagination
from .permissions import IsModerator, IsOwner, NotModerator, ModeratorOrOwner
from .serializers import CourseSerializer, LessonSerializer


class CourseViewSet(viewsets.ModelViewSet):
    """ViewSet для работы с курсами."""

    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = MaterialsPagination

    def get_permissions(self):
        """Определяет права доступа для разных действий."""
        if self.action in ['create', 'destroy']:
            return [IsAuthenticated(), NotModerator()]
        if self.action in ['update', 'partial_update']:
            return [IsAuthenticated(), ModeratorOrOwner()]
        return [IsAuthenticated()]

    def perform_create(self, serializer) -> None:
        """Сохраняет владельца при создании курса."""
        serializer.save(owner=self.request.user)


class LessonDetailView(generics.RetrieveAPIView):
    """Контроллер для просмотра урока."""

    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
    permission_classes = [IsAuthenticated]


class LessonUpdateView(generics.UpdateAPIView):
    """Контроллер для обновления урока."""

    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
    permission_classes = [IsAuthenticated, IsOwner | IsModerator]
    pagination_class = MaterialsPagination


class LessonDeleteView(generics.DestroyAPIView):
    """Контроллер для удаления урока."""

    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
    permission_classes = [IsAuthenticated, IsOwner]


class CourseSubscriptionView(APIView):
    """Управление подпиской на курс"""

    def post(self, request, *args, **kwargs):
        user = request.user
        course_id = request.data.get('course_id')

        if not course_id:
            return Response({"error": "Не указан ID курса"}, status=400)

        course_item = get_object_or_404(Course, pk=course_id)
        subs_item = CourseSubscription.objects.filter(user=user, course=course_item)

        # Если подписка есть - удаляем
        if subs_item.exists():
            subs_item.delete()
            message = 'подписка удалена'
        # Если подписки нет - создаем
        else:
            CourseSubscription.objects.create(user=user, course=course_item)
            message = 'подписка добавлена'

        return Response({"message": message})


# В файле views.py добавьте:

class LessonListCreateView(generics.ListCreateAPIView):
    """Контроллер для просмотра списка уроков и создания уроков."""
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = MaterialsPagination

    def perform_create(self, serializer):
        """Сохраняет владельца при создании урока."""
        serializer.save(owner=self.request.user)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            print(f"Validation errors: {serializer.errors}")
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
