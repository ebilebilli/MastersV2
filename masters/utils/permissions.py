from rest_framework.permissions import BasePermission 
from rest_framework import permissions


class HeHasPermission(BasePermission):   
    """
    Custom permission to allow access only if the requesting user
    is the owner of the object or is a staff member.
    """
    def has_object_permission(self, request, view, obj):
        return request.user == obj.user or request.user.is_staff


