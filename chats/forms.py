from django.forms import ModelForm, modelformset_factory, formset_factory
from django import forms
from .models import ChatRoom, Message


class ChatRoomForm(ModelForm):
    class Meta:
        model = ChatRoom
        fields = ["name", "members"]


ChatRoomFormSet = modelformset_factory(
    ChatRoom,
    fields=['name', 'members'],
    extra=0
)

class MessageForm(ModelForm):
    class Meta:
        model = Message
        fields = ["sender", "content", "read"]


MessageFormSet = modelformset_factory(
    Message,
    fields = ['sender', 'content', 'read'],
    extra=0,
    widgets={
        'sender': forms.TextInput(attrs={'readonly': True}),
        'content': forms.Textarea(attrs={'readonly': True, 'rows': 2}),
    }
)