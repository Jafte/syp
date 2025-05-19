from django.http import Http404, HttpResponseRedirect
from django.urls import reverse
from django.utils import timezone
from django.views.generic import ListView, DetailView, CreateView, UpdateView

from rest_framework import permissions
from rest_framework.generics import ListAPIView, CreateAPIView

from plans.forms import EventAttendeeRequestActionForm, EventAttendeeRequestCreateForm
from plans.models import Event, EventAttendeeRequest, EventAttendee
from plans.serializers import EventSerializer


class UserEventsListView(ListAPIView):
    serializer_class = EventSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Event.objects.filter(creator=self.request.user)


class AddUserEventView(CreateAPIView):
    serializer_class = EventSerializer

    def perform_create(self, serializer):
        serializer.save(creator=self.request.user)



class EventDetailView(DetailView):
    model = Event
    template_name = 'plans/event_detail.html'
    pk_url_kwarg = 'event_id'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        attendee_requests = EventAttendeeRequest.objects.filter(event=self.object, sender=self.request.user)
        active_attendee_requests = attendee_requests.filter(accepted_at__isnull=True, rejected_at__isnull=True)
        accepted_attendee_requests = attendee_requests.filter(accepted_at__isnull=False)
        context['accepted_attendee_requests'] = accepted_attendee_requests
        context['can_send_attendee_requests'] = not active_attendee_requests.exists() and not accepted_attendee_requests.exists()
        return context


class EventAttendeeRequestActionFormView(UpdateView):
    model = EventAttendeeRequest
    form_class = EventAttendeeRequestActionForm
    template_name = 'plans/event_attendee_request_form.html'
    pk_url_kwarg = 'request_id'
    queryset = EventAttendeeRequest.objects.filter(accepted_at__isnull=True, rejected_at__isnull=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.event = None

    def dispatch(self, request, *args, **kwargs):
        event_id = kwargs.get('event_id')
        try:
            self.event = Event.objects.get(pk=event_id, creator=request.user)
        except Event.DoesNotExist:
            raise Http404("Event does not exist")
        return super().dispatch(request, *args, **kwargs)

    def get_object(self, queryset=None):
        object = super().get_object(queryset)
        if object.event != self.event:
            raise Http404("Event does not exist")
        if EventAttendee.objects.filter(event=self.event, user=object.sender).exists():
            raise Http404("User is already an attendee")
        return object

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['event'] = self.event
        return context

    def form_valid(self, form):

        if form.cleaned_data['action'] == 'accept':
            form.instance.accepted_at = timezone.now()
            form.instance.save()
            EventAttendee.objects.create(
                event=self.event,
                user=form.instance.sender
            )
        elif form.cleaned_data['action'] == 'reject':
            form.instance.rejected_at = timezone.now()
            form.instance.save()

        return HttpResponseRedirect(self.get_success_url())

    def get_success_url(self):
        return reverse('event_detail', kwargs={'event_id': self.event.id})


class EventAttendeeRequestCreateFormView(CreateView):
    model = EventAttendeeRequest
    template_name = 'plans/event_attendee_request_form.html'
    form_class = EventAttendeeRequestCreateForm

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.event = None

    def dispatch(self, request, *args, **kwargs):
        event_id = kwargs.get('event_id')
        try:
            self.event = Event.objects.get(pk=event_id)
        except Event.DoesNotExist:
            raise Http404("Event does not exist")
        if EventAttendee.objects.filter(event=self.event, user=request.user).exists():
            raise Http404("User is already an attendee")
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['event'] = self.event
        return context

    def form_valid(self, form):
        form.instance.event = self.event
        form.instance.sender = self.request.user
        form.save()
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('event_detail', kwargs={'event_id': self.event.id})
