from datetime import date

from django.contrib.auth import get_user_model
from django.utils.translation import ugettext_lazy as ugl

from rest_framework import serializers
from rest_framework.reverse import reverse

from scrum.board.models import Sprint, Task


User = get_user_model()


class SprintSerializer(serializers.ModelSerializer):
    links = serializers.SerializerMethodField('find_links')

    class Meta:
        model = Sprint
        fields = ('id', 'name', 'description', 'end', 'links', )

    def find_links(self, obj):
        request = self.context['request']

        return {
            'self': reverse('sprint-detail', kwargs={'pk': obj.pk}, request=request),
            'tasks': reverse('task-list', request=request) + '?sprint={}'.format(obj.pk),
        }
    
    def validate_end(self, value):
        new = self.instance is None
        updated = not new and self.initial_data['end'] != self.instance.end
        if (new or updated) and (value < date.today()):
            msg = ugl('End date cannot be in the past.')
            raise serializers.ValidationError(msg)
        return attrs


class TaskSerializer(serializers.ModelSerializer):
    assigned = serializers.SlugRelatedField(
        slug_field=User.USERNAME_FIELD, required=False, queryset=User.objects.all())
    status_display = serializers.SerializerMethodField('find_status_display')
    links = serializers.SerializerMethodField('find_links')

    class Meta:
        model = Task
        fields = ('id', 'name', 'description', 'sprint', 'status_display', 'order',
                  'assigned', 'started', 'due', 'completed', 'links', )

    def find_status_display(self, obj):
        return obj.get_status_display()

    def find_links(self, obj):
        request = self.context['request']

        links = {
            'self': reverse('task-detail', kwargs={'pk': obj.pk}, request=request),
            'sprint': None,
            'assigned': None,
        }

        if obj.sprint_id:
            links['sprint'] = reverse('sprint-detail', 
                kwargs={'pk': obj.sprint_id}, request=request)
        if obj.assigned:
            links['assigned'] = reverse('user-detail', 
                kwargs={User.USERNAME_FIELD: obj.assigned}, request=request)
        return links

    def validate_sprint(self, value):
        orig_task = getattr(self, 'instance', None)
        orig_sprint = getattr(orig_task, 'sprint', None)
        sprint = value
        if (getattr(orig_sprint, 'id', None) != getattr(sprint, 'id', None) and
                int(self.initial_data['status']) == Task.STATUS_DONE):
            raise serializers.ValidationError(_('Cannot change the sprint of a completed task.'))
        if getattr(sprint, 'end', date.today()) < date.today():
            raise serializers.ValidationError(_('Cannot assign tasks to past sprints'))
        return value

    def validate(self, data):
        sprint = data.get('sprint', None)
        status = data.get('status', None)
        started = data.get('started', None)
        completed = data.get('completed', None)
        if not sprint and status != Task.STATUS_TODO:
            raise serializers.ValidationError(_('Backlog tasks must have "Not Started" status.'))
        if started and status == Task.STATUS_TODO:
            raise serializers.ValidationError(_('"Not Started" tasks cannot have a start date.'))
        if completed and status != Task.STATUS_DONE:
            raise serializers.ValidationError(
                _('Completed date cannot be set for incomplete tasks.'))
        if status == Task.STATUS_DONE and not completed:
            raise serializers.ValidationError(_('Completed tasks must have a completed date'))
        return data


class UserSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(source='get_full_name', read_only=True)
    links = serializers.SerializerMethodField('find_links')

    class Meta:
        model = User
        field = ('id', User.USERNAME_FIELD, 'full_name', 'is_active', 'links', )

    def find_links(self, obj):
        request = self.context['request']
        username = obj.get_username()

        return {
            'self': reverse('user-detail', kwargs={User.USERNAME_FIELD: username}, request=request),
            'tasks': '{}?assigned={}'.format(
                reverse('task-list', request=request), username)
        }
