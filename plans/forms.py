from django import forms

from plans.models import EventAttendeeRequest


class EventAttendeeRequestActionForm(forms.ModelForm):
    action = forms.ChoiceField(choices=[('accept', 'Accept'), ('reject', 'Reject')])
    class Meta:
        model = EventAttendeeRequest
        fields = ['action']

class EventAttendeeRequestCreateForm(forms.ModelForm):
    class Meta:
        model = EventAttendeeRequest
        fields = ['comment']
