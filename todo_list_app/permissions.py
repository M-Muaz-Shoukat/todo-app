from rest_framework import permissions

from rest_framework import permissions


class IsOwner(permissions.BasePermission):

    def __init__(self, user_path):
        self.user_path = user_path

    def has_object_permission(self, request, view, obj):

        user_path_parts = self.user_path.split('.')
        current_obj = obj
        for part in user_path_parts:
            current_obj = getattr(current_obj, part, None)
            if current_obj is None:
                return False
        return current_obj == request.user

