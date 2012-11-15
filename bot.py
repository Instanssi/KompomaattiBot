# -*- coding: utf-8 -*-

# Import libs
from twisted.words.protocols import irc
from twisted.internet import reactor, protocol
import os,sys
from datetime import datetime

# Import configuration
import config

# Django environment
sys.path.append(config.DJANGO_ROOT)
os.environ['DJANGO_SETTINGS_MODULE'] = config.DJANGO_SETTINGS

# Import django model
from Instanssi.screenshow.models import IRCMessage

# Helper decode function
def decode(bytes):
    try:
        text = bytes.decode('utf-8')
    except UnicodeDecodeError:
        try:
            text = bytes.decode('iso-8859-1')
        except UnicodeDecodeError:
            text = bytes.decode('cp1252')
    return text

# Bot itself
class KompomaattiBot(irc.IRCClient):
    def _get_nickname(self):
        return self.factory.nickname
    nickname = property(_get_nickname)

    def connectionMade(self):
        irc.IRCClient.connectionMade(self)
        print "Connected to", self.factory.host, ':', self.factory.port
    
    def signedOn(self):
        self.join(self.factory.channel)
        print "Signed on as", self.nickname

    def joined(self, channel):
        print "Joined channel", channel
        
    def privmsg(self, user, channel, msg):
        # Skip private messages
        if channel == self.nickname:
            return

        # Save message
        message = IRCMessage()
        message.event_id = config.EVENT_ID
        message.date = datetime.now()
        message.message = unicode(decode(msg))
        message.nick = unicode(decode(user.split('!', 1)[0]))
        message.save()
        
# Factory for bots
class LogBotFactory(protocol.ClientFactory):
    def __init__(self):
        self.channel = config.CHANNEL
        self.nickname = config.NICK
        self.host = config.SERVER
        self.port = config.PORT

    def buildProtocol(self, addr):
        bot = KompomaattiBot()
        bot.factory = self
        return bot

    def clientConnectionLost(self, connector, reason):
        print "Connection lost: ", reason
        connector.connect()

    def clientConnectionFailed(self, connector, reason):
        print "Connection failed: ", reason
        reactor.stop()
        
    def clientConnectionFailed(self, connector, reason):
        print "Could not connect: ", reason
        
if __name__ == '__main__':
    botfactory = LogBotFactory()
    reactor.connectTCP(config.SERVER, config.PORT, botfactory)
    reactor.run()
    