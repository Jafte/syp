import decimal

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


class RoundingDecimalField(serializers.DecimalField):

    def validate_precision(self, value):
        # This is needed to avoid to raise an error if `value` has more decimals than self.decimal_places.
        with decimal.localcontext() as ctx:
            if self.rounding:
                ctx.rounding = self.rounding
            value = round(value, self.decimal_places)
        return super().validate_precision(value)


class EventSerializer(serializers.ModelSerializer):
    creator = UserSerializer(required=False)
    started_at = serializers.DateTimeField(required=False, allow_null=True)
    ended_at = serializers.DateTimeField(required=False, allow_null=True)
    attendees_count = serializers.SerializerMethodField()
    location_lat = RoundingDecimalField(max_digits=9, decimal_places=6)
    location_long = RoundingDecimalField(max_digits=9, decimal_places=6)
    class Meta:
        model = Event
        fields = [
            'id',
            'creator',
            'title',
            'description',
            'attendees_count',
            'created_at',
            'started_at',
            'ended_at',
            'location_text',
            'location_lat',
            'location_long'
        ]
        read_only_fields = ('id', 'creator', 'attendees_count', 'created_at')

    def get_attendees_count(self, event):
        return event.attendees.count()

    def validate_started_at(self, value):
        if not value:
            return None
        return value

    def validate_ended_at(self, value):
        if not value:
            return None
        return value


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

