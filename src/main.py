# -*- coding: utf-8 -*-

# Attempt to find configuration
try:
    import config
except:
    print "Config module not found! Remember to rename config.py-dist to config.py!"
    exit()
    
# Library imports
import os,sys

# Django environment
sys.path.append(config.DJANGO_ROOT)
os.environ['DJANGO_SETTINGS_MODULE'] = config.DJANGO_SETTINGS

# Other imports
from bot import LogBotFactory, BotException
from twisted.internet import reactor

# Main
if __name__ == '__main__':
    try:
        botfactory = LogBotFactory(config.CHANNEL, config.NICK, config.SERVER, config.PORT, config.EVENT_ID)
    except BotException as ex:
        print "Exception:",ex.value
        exit()
        
    reactor.connectTCP(config.SERVER, config.PORT, botfactory)
    reactor.run()