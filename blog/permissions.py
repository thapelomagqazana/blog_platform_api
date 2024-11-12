from rest_framework.permissions import BasePermission

class IsAuthorPermission(BasePermission):
    """
    Custom permission to allow only the author of a blog post to edit it.
    """
    def has_object_permission(self, request, view, obj):
        return obj.author == request.user
