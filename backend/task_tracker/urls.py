from django.urls import path
from . import views


urlpatterns = [
    path('team/', views.TeamViewSet.as_view({
        'post': 'create',
    }), name="team"),
    path('availability/<int:team_id>/', views.TeamViewSet.as_view({
        'get': 'availability',
    }), name="team-availability"),
    path('task/', views.TaskViewSet.as_view({
        'post': 'create'
    }), name="task-list"),
    path('task/<int:pk>/', views.TaskViewSet.as_view({
        'patch': 'partial_update',
    }), name="task-detail"),
    path('report/', views.TaskViewSet.as_view({
        'get': 'report'
    }), name="report"),
]