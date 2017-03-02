# -*- coding: utf-8 -*-

import os
import sys
import django
import irc3
from .django_integration import django_log_add, django_log_cleanup

# Attempt to find configuration
try:
    import config
except ImportError:
    print("Config module not found! Remember to rename config.py-dist to config.py!")
    exit()

# Django environment
sys.path.append(config.DJANGO_ROOT)
os.environ['DJANGO_SETTINGS_MODULE'] = config.DJANGO_SETTINGS


@irc3.plugin
class KompomaattiBot:
    requires = [
        'irc3.plugins.core',
        'irc3.plugins.command',
        'irc3.plugins.human',
    ]

    def __init__(self, bot):
        self.bot = bot
        self.log = self.bot.log
        self.channel = None

    def connection_made(self):
        self.log.info("Connected")

    def server_ready(self):
        self.log.info("Server ready")

    def connection_lost(self):
        self.log.info("Connection lost")

    @irc3.event(irc3.rfc.JOIN)
    def joined(self, mask, channel, **kw):
        self.log.info("Joined channel '%s'", channel)
        self.channel = channel

    @irc3.event(irc3.rfc.PRIVMSG)
    def privmsg(self, mask=None, data=None, **kw):
        nick = mask.nick
        target = kw.get('target')
        self.log.info("%s @ %s: '%s'", nick, target, data)
        if target == self.channel:
            django_log_cleanup()
            django_log_add(nick, data, config.EVENT_ID)


def main():
    bot_conf = dict(
        nick=config.NICK,
        autojoins=[config.CHANNEL],
        host=config.SERVER, port=config.PORT, ssl=False,
        includes=[
            'irc3.plugins.core',
            'irc3.plugins.command',
            'irc3.plugins.human',
            __name__,
        ]
    )
    bot = irc3.IrcBot.from_config(bot_conf)
    bot.run(forever=True)


if __name__ == '__main__':
    django.setup()
    main()
