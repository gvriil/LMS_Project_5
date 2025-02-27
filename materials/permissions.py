from rest_framework.permissions import BasePermission


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