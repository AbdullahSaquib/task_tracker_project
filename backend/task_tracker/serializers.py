from rest_framework import serializers
from task_tracker.models import Team, Task


class TeamSerializer(serializers.ModelSerializer):

    class Meta:
        model = Team
        fields = ["name", "members"]


class TaskSerializer(serializers.ModelSerializer):

    class Meta:
        model = Task
        fields = ["name", "priority", "team_members", "start_date", "end_date", 
            "status"]

    def validate_team_members(self, value):
        """Check team members are available"""
        if Task.objects.filter(
            team_members__in=value,
            status__in=Task.BUSY_STATUS
        ).exists():
            raise serializers.ValidationError("Team member is not available")
        return value


class MemberTaskUpdateSerializer(serializers.ModelSerializer):

    class Meta:
        model = Task
        fields = ["status"]


class ReportTaskSerializer(serializers.ModelSerializer):

    class Meta:
        model = Task
        fields = ["name", "team_members", "status"]


class DateSerializer(serializers.Serializer):
    date = serializers.DateField()
