# -*- coding: utf-8 -*-

# Libraries
from datetime import datetime,timedelta
import utils

# Import django model
from Instanssi.screenshow.models import IRCMessage

def django_log_cleanup():
    filterdate = datetime.now() - timedelta(days=1)
    IRCMessage.objects.filter(date__lt=filterdate).delete()
    
def django_log_add(user, msg, event_id):
    try:
        message = IRCMessage()
        message.event_id = event_id
        message.date = datetime.now()
        message.message = unicode(utils.decode(msg))
        message.nick = unicode(utils.decode(user))
        message.save()
    except UnicodeDecodeError:
        return False
    return True