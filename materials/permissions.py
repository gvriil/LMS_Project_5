from rest_framework import status
from rest_framework.permissions import BasePermission

from users.models import User


class IsModerator(BasePermission):
    """Проверка на модератора."""

    def has_permission(self, request, view):
        return request.user.groups.filter(name='moderators').exists()

    def has_object_permission(self, request, view, obj):
        return self.has_permission(request, view)


class IsOwner(BasePermission):
    """Проверка на владельца объекта."""

    def has_object_permission(self, request, view, obj):
        return obj.owner == request.user


class NotModerator(BasePermission):
    """Проверка, что пользователь не модератор."""

    def has_permission(self, request, view):
        return not IsModerator().has_permission(request, view)

    def has_object_permission(self, request, view, obj):
        return self.has_permission(request, view)


class ModeratorOrOwner(BasePermission):
    """Проверка, что пользователь является модератором или владельцем."""

    def has_permission(self, request, view):
        return IsModerator().has_permission(request, view)

    def has_object_permission(self, request, view, obj):
        return (
            IsModerator().has_object_permission(request, view, obj) or
            IsOwner().has_object_permission(request, view, obj)
        )

def test_lesson_access_by_nonowner(self):
    # Создаем второго пользователя
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
    # Создаем модератора, который не является владельцем
    new_moderator = User.objects.create_user(
        email='mod2@example.com',
        password='password',
        role='moderator'
    )
    self.client.force_authenticate(user=new_moderator)

    # Пытаемся удалить чужой урок (проверка is_staff в IsOwnerOrReadOnly)
    url = f'/api/lessons/{self.lesson.id}/delete/'
    response = self.client.delete(url)
    self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)