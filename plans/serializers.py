from rest_framework import serializers

from plans.models import Event, EventAttendee, EventAttendeeRequest
from users.serializers import UserSerializer


class DetailEventSerializer(serializers.ModelSerializer):
    creator = UserSerializer()
    attendees = serializers.SerializerMethodField()
    requests = serializers.SerializerMethodField()
    class Meta:
        model = Event
        fields = ['id', 'creator', 'title', 'created_at', 'description', 'started_at', 'ended_at', 'location']

    def get_attendees(self, event):
        return EventAttendeeSerializer(event.attendees.all(), many=True).data

    def get_requests(self, event):
        return EventAttendeeRequestSerializer(event.action_required_requests(), many=True).data


class EventSerializer(serializers.ModelSerializer):
    creator = UserSerializer()
    attendees_count = serializers.SerializerMethodField()
    class Meta:
        model = Event
        fields = ['id', 'creator', 'title', 'attendees_count', 'created_at', 'description', 'started_at', 'ended_at', 'location']
        read_only_fields = ('id', 'creator', 'attendees_count', 'created_at')

    def get_attendees_count(self, event):
        return event.attendees.count()


class EventAttendeeSerializer(serializers.ModelSerializer):
    user = UserSerializer()
    event = EventSerializer()
    class Meta:
        model = EventAttendee
        fields = ['id', 'event', 'user', 'created_at']


class EventAttendeeRequestSerializer(serializers.ModelSerializer):
    sender = UserSerializer()
    event = EventSerializer()
    class Meta:
        model = EventAttendeeRequest
        fields = ['id', 'event', 'sender', 'comment', 'created_at', 'accepted_at', 'rejected_at']

