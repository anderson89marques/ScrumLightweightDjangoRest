from django.conf import settings
from django.db import models
from django.utils.translation import ugettext_lazy as tl


class Sprint(models.Model):
    """Development interation period"""

    name = models.CharField(max_length=100, blank=True, default='')
    description = models.TextField(blank=True, default='')
    end = models.DateField(unique=True)

    def __str__(self):
        return self.name or tl('Sprint ending %s') % self.end


class Task(models.Model):
    """Unit of work to be done for the sprint"""

    STATUS_TODO = 1
    STATUS_IN_PROGRESS = 2
    STATUS_TESTING = 3
    STATUS_DONE = 4

    STATUS_CHOICES = (
        (STATUS_TODO, tl('Not stated')),
        (STATUS_IN_PROGRESS, tl('In progress')),
        (STATUS_TESTING, tl('Testing')),
        (STATUS_DONE, tl('Done')),
    )

    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, default='')
    sprint = models.ForeignKey(Sprint, blank=True, null=True)
    status = models.SmallIntegerField(
        choices=STATUS_CHOICES, default=STATUS_TODO)
    order = models.SmallIntegerField(default=0)
    assigned = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True)
    started = models.DateField(blank=True, null=True)
    due = models.DateField(blank=True, null=True)
    completed = models.DateField(blank=True, null=True)

    def __str__(self):
        return self.name
