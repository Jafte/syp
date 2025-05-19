from django.contrib import admin
from plans.models import Event, EventAttendee, EventAttendeeRequest


class EventAttendeeInline(admin.TabularInline):
    model = EventAttendee
    raw_id_fields = ('user',)
    extra = 1


class EventAttendeeRequestInline(admin.TabularInline):
    model = EventAttendeeRequest
    raw_id_fields = ('sender',)
    extra = 1


@admin.register(Event)
class PlanAdmin(admin.ModelAdmin):
    list_display = ('creator', 'title', 'started_at', 'ended_at', 'location_text', 'location_lat', 'location_long')
    raw_id_fields = ('creator',)
    inlines = [EventAttendeeInline, EventAttendeeRequestInline]