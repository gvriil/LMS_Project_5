from rest_framework import generics, viewsets
from rest_framework.permissions import IsAuthenticated

from .models import Course, Lesson
from .permissions import IsModerator, IsOwner, NotModerator, ModeratorOrOwner
from .serializers import CourseSerializer, LessonSerializer


class CourseViewSet(viewsets.ModelViewSet):
    """ViewSet для работы с курсами."""

    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    permission_classes = [IsAuthenticated]

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


class LessonCreateView(generics.CreateAPIView):
    """Контроллер для создания уроков."""

    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer) -> None:
        """Сохраняет владельца при создании урока."""
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


class LessonDeleteView(generics.DestroyAPIView):
    """Контроллер для удаления урока."""

    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
    permission_classes = [IsAuthenticated, IsOwner]