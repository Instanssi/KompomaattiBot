# -*- coding: utf-8 -*-

# Import twisted
from twisted.words.protocols import irc
from twisted.internet import reactor, protocol
from django_integration import *

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
        short_name = user.split('!', 1)[0]
        
        # Skip private messages
        if channel == self.nickname:
            if msg == 'help':
                self.msg(user, "--- Command list ---")
                self.msg(user, " * help      Prints this help.")
                self.msg(user, " * version   Prints bot version information")
                self.msg(user, " * events    Prints list of next 5 upcoming events")
            elif msg == 'version':
                self.msg(user, "KompomaattiBot v0.1 by Katajakasa")
            elif msg == 'events':
                for event in django_get_upcoming(self.factory.event):
                    time = event['date'].strftime("%d.%m.%Y klo. %H:%I")
                    ostr = time+" - "+event['title']
                    self.msg(user, ostr.encode( "utf-8" ))
            else:
                self.msg(user, "Unidentified command. Use command \"help\" for commands list.")
                
            print "Received command",msg,"from",short_name
        else:
            # Remove old messages
            if self.factory.cleanup_test >= self.factory.cleanup_limit:
                django_log_cleanup()
                self.factory.cleanup_test = 0
            else:
                self.factory.cleanup_test += 1
        
            # Write to log
            django_log_add(short_name, msg, self.factory.event_id)

        
class BotException(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)
        
# Factory for bots
class LogBotFactory(protocol.ClientFactory):
    def __init__(self, channel, nickname, host, port, event_id):
        self.channel = channel
        self.nickname = nickname
        self.host = host
        self.port = port
        self.event_id = event_id
        self.cleanup_test = 0
        self.cleanup_limit = 20
        self.event = django_get_event(self.event_id)
        if self.event == None:
            raise BotException("Event not found!")

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
        