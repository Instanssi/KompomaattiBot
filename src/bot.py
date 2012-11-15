# -*- coding: utf-8 -*-

# Import twisted
from twisted.words.protocols import irc
from twisted.internet import reactor, protocol
from django_integration import django_log_add, django_log_cleanup

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
            # Implement help and other stuff later ...
            if msg == 'help':
                print 'User',user,'is asking for help.'
            return

        # Remove old messages
        if self.factory.cleanup_test >= self.factory.cleanup_limit:
            django_log_cleanup()
            self.factory.cleanup_test = 0
        else:
            self.factory.cleanup_test += 1
    
        # Write to log
        django_log_add(user.split('!', 1)[0], msg, self.factory.event_id)

        
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
        