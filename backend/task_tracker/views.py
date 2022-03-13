from rest_framework import mixins
from rest_framework import generics
from rest_framework.decorators import action
from rest_framework import viewsets
from rest_framework.response import Response
from task_tracker.serializers import TeamSerializer, TaskSerializer, MemberTaskUpdateSerializer, ReportTaskSerializer, DateSerializer
from task_tracker.models import Team, Task, User
from task_tracker.permissions import IsTeamLeader, IsTeamMember, IsPatch
from task_tracker.renderers import TeamRenderer, TaskRenderer
from django.shortcuts import get_object_or_404
from django.db.models import Case, When


class TeamViewSet(viewsets.ModelViewSet):
    """Create team using user ids"""
    queryset = Team.objects.all()
    serializer_class = TeamSerializer
    permission_classes = [IsTeamLeader]
    renderer_classes = [TeamRenderer]

    def perform_create(self, serializer):
        """Get team leader from request"""
        serializer.save(leader=self.request.user)

    @action(detail=True)
    def availability(self, request, team_id):
        """Get list of team members and their availability"""
        result = {}  # {<email>: True/False, ...}
        users = User.objects\
            .filter(team__id=team_id)\
            .annotate(availability=Case(
                When(task__status__in=Task.BUSY_STATUS, then=True),
                default=False
            )).values("email", "availability")
        for user in users:
            result[user["email"]] = user["availability"]
        return Response(result)


class TaskViewSet(viewsets.ModelViewSet):
    """Create task and assign it to users"""
    queryset = Task.objects.all()
    permission_classes = [IsTeamLeader|(IsTeamMember & IsPatch)]
    renderer_classes = [TaskRenderer]

    def get_serializer_class(self):
        """Get serializer class depending on user type"""
        if self.request.user.is_team_leader:
            return TaskSerializer
        else:
            return MemberTaskUpdateSerializer

    def perform_create(self, serializer):
        """Get team leader from request"""
        serializer.save(team_leader=self.request.user)
    
    @action(detail=False)
    def report(self, request):
        """Get list of tasks whose status were changed on given date"""
        date_serializer = DateSerializer(data=request.GET)
        if date_serializer.is_valid():
            date = date_serializer.validated_data["date"]
            serializer = ReportTaskSerializer(Task.objects.filter(
                team_leader=request.user, status_updated_at__date=date),
                many=True)
            return Response(serializer.data, status=200)
        return Response(date_serializer.errors, status=400)

