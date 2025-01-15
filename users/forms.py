from django import forms


class FriendshipAction(forms.Form):
    action = forms.ChoiceField(choices=[
        ('send_request', 'Send request'),
        ('cancel_request', 'Cancel request'),
        ('accept_request', 'Accept request'),
        ('reject_request', 'Reject request'),
        ('remove_from_friends', 'Remove from friends')
    ])
    comment = forms.CharField(widget=forms.Textarea(attrs={'rows': 3}), required=False)
