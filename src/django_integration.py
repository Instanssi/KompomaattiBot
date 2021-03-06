# -*- coding: utf-8 -*-

# Libraries
from django.utils import timezone

# Django stuff
from Instanssi.kompomaatti.misc.events import get_upcoming
from Instanssi.screenshow.models import IRCMessage
from Instanssi.kompomaatti.models import Event


def django_get_event(event_id):
    try:
        return Event.objects.get(pk=event_id)
    except Event.DoesNotExist:
        return None


def django_get_upcoming(event):
    return get_upcoming(event)[:5]


def django_log_cleanup():
    limit = 50
    n = 0
    last_id = 0
    for msg in IRCMessage.objects.all().order_by('-id'):
        last_id = msg.id
        if n >= limit:
            break
        n += 1
    
    IRCMessage.objects.filter(id__lt=last_id).delete()


def django_log_add(user, msg, event_id):
    try:
        message = IRCMessage()
        message.event_id = event_id
        message.date = timezone.now()
        message.message = msg
        message.nick = user
        message.save()
    except UnicodeDecodeError:
        return False
    return True
