from django.db import models

from users.models import User


class Event(models.Model):
    creator = models.ForeignKey(User, on_delete=models.CASCADE, related_name="created_events")
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    started_at = models.DateTimeField(null=True, blank=True)
    ended_at = models.DateTimeField(null=True, blank=True)
    location = models.CharField(max_length=200, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def action_required_requests(self):
        return self.requests.filter(accepted_at__isnull=True, rejected_at__isnull=True)


class EventAttendee(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name="attendees")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="events")
    created_at = models.DateTimeField(auto_now_add=True)


class EventAttendeeRequest(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name="requests")
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name="sent_event_invitations")
    comment = models.TextField(blank=True)
    accepted_at = models.DateTimeField(null=True, blank=True)
    rejected_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
