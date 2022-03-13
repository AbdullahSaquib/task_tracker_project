from rest_framework.permissions import BasePermission


class IsTeamLeader(BasePermission):
    """
    Custom permission to only allow team leader
    """

    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.is_team_leader)


class IsTeamMember(BasePermission):
    """
    Custom permission to only allow team member
    """

    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and (not request.user.is_team_leader))


class IsPatch(BasePermission):
    """
    The request method is patch
    """

    def has_permission(self, request, view):
        return request.method == "PATCH"

