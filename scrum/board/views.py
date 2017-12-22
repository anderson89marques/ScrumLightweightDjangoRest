from django.contrib.auth import get_user_model

from django_filters.rest_framework import DjangoFilterBackend 
from rest_framework import authentication, permissions, viewsets, filters

from scrum.board.forms import TaskFilter, SprintFilter
from scrum.board.models import Sprint, Task
from scrum.board.serializers import SprintSerializer, TaskSerializer, UserSerializer

User = get_user_model()


class DefaultsMixin:
    """Default settings for view authentication, permissions, 
    fitering and pagination"""

    authentication_classes = (
        authentication.BasicAuthentication,
        authentication.TokenAuthentication,
    )
    permission_classes = (
        permissions.IsAuthenticated,
    )
    paginate_by = 25
    paginate_by_param = 'page_size'
    max_paginate_by = 100
    filter_backends = (
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter
    )

class SprintViewSet(DefaultsMixin, viewsets.ModelViewSet):
    """API endpoint for listing and creating sprints"""

    queryset = Sprint.objects.order_by('end')
    serializer_class = SprintSerializer
    filter_class = SprintFilter
    search_fields = ('name', )
    ordering_fields = ('end', 'name', )

class TaskViewSet(DefaultsMixin, viewsets.ModelViewSet):
    """API endpoint to listing and creating tasks"""

    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    filter_class = TaskFilter
    search_fields = ('name', 'description', )
    ordering_fields = ('name', 'order', 'started', 'due', 'completed', )


class UserViewSet(DefaultsMixin, viewsets.ReadOnlyModelViewSet):
    """API endpoint to listing users"""

    lookup_field = User.USERNAME_FIELD
    lookup_url_kwarg = User.USERNAME_FIELD
    queryset = User.objects.order_by(User.USERNAME_FIELD)
    serializer_class = UserSerializer
    search_fields = (User.USERNAME_FIELD, )