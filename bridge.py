# -*- coding: iso-8859-1 -*-

#
# Bridge
#   Tunnel messages from one channel to another. Useful for example
#   IRC channels with non ascii chars in channel name, when different
#   encodings actually form up different channels. 
#

# Copyright (C) 2008 Harri Hämäläinen <hhamalai@iki.fi>
#
#
# Permission is hereby granted, free of charge, to any person
# obtaining a copy of this software and associated documentation files
# (the "Software"), to deal in the Software without restriction,
# including without limitation the rights to use, copy, modify, merge,
# publish, distribute, sublicense, and/or sell copies of the Software,
# and to permit persons to whom the Software is furnished to do so,
# subject to the following conditions:
#
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
# IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY
# CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
# TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
# SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

from plugin import Plugin

info = 'Bridge plugin'

class Bridge(Plugin):
    def __init__(self, connection, plugin_config=dict()):
        self.tunnels = plugin_config.get('tunnels', [])
        self.connection = connection
        self.configuration = plugin_config
       
    def do_chanmsg(self, nick, ident, host, channel, msg):
        if channel not in self.configuration['tunnels'].keys():
            return
        for tunnel in self.tunnels:
            if tunnel == channel:
                continue
            converted_msg = self.convert(msg, self.tunnels[channel]['target'])
            self.connection.send_to('PRIVMSG %s :<%s> %s \n' % (tunnel, nick, converted_msg))
    
    def do_join(self, nick, ident, host, channel):
        if channel not in self.configuration['tunnels'].keys():
            return
        for tunnel in self.tunnels:
            if tunnel == channel:
                continue
            self.connection.send_to('PRIVMSG %s : %s has joined %s \n' % (self.tunnels[channel]['target'], nick, channel))
    
    def do_part(self, nick, ident, host, channel, msg):
        if channel not in self.configuration['tunnels'].keys():
            return
        for tunnel in self.tunnels:
            if tunnel == channel:
                continue
            converted_msg = self.convert(msg, self.tunnels[channel]['target'])
            self.connection.send_to('PRIVMSG %s :%s left %s (%s) \n' % (self.tunnels[channel]['target'], nick, channel, converted_msg))

    def do_action(self, nick, ident, host, channel, msg):
        if channel not in self.configuration['tunnels'].keys():
            return
        for tunnel in self.tunnels:
            if tunnel == channel:
                continue
            converted_msg = self.convert(msg, self.tunnels[channel]['target'])
            self.connection.send_to('PRIVMSG %s :%sACTION %s %s %s\n' % (self.tunnels[channel]['target'], '\x01', nick, converted_msg, '\x01'))
    
    def do_topic(self, nick, ident, host, channel, msg):
        if channel not in self.configuration['tunnels'].keys():
            return
        if nick == self.connection.identity.nick:
            return
        for tunnel in self.tunnels:
            if tunnel == channel:
                continue
            converted_msg = self.convert(msg, self.tunnels[channel]['target'])
            self.connection.send_to('TOPIC %s :%s \n' % (self.tunnels[channel]['target'], converted_msg))
    
    def do_kick(self, kicker, ident, host, channel, nick, msg):
        if channel not in self.configuration['tunnels'].keys():
            return
        for tunnel in self.tunnels:
            if tunnel == channel:
                continue
            converted_msg = self.convert(msg, self.tunnels[channel]['target'])
            self.connection.send_to('PRIVMSG %s :%s was kicked by %s (%s) \n' % (self.tunnels[channel]['target'], nick, kicker, converted_msg))
    
    def do_quit(self, nick, ident, host, msg):
        for tunnel in self.tunnels:
            if not nick in self.connection.chatters[tunnel]:
                continue
            converted_msg = self.convert(msg, self.tunnels[tunnel]['target'])
            self.connection.send_to('PRIVMSG %s :%s has quit (%s) \n' % (self.tunnels[tunnel]['target'], nick, msg))
    
    def do_nick(self, nick,  ident, host, new_nick):
        for tunnel in self.tunnels:
            if not nick in self.connection.chatters[tunnel]:
                continue
            self.connection.send_to('PRIVMSG %s :%s is now known as %s \n' %  (self.tunnels[tunnel]['target'], nick, new_nick))

    def do_output(self, message, channel):
        if channel not in self.configuration['tunnels'].keys():
            return
        for tunnel in self.tunnels:
            if tunnel == channel:
                continue
            converted_msg = self.convert(message, self.tunnels[channel]['target'])
            self.connection.send_to(converted_msg)

    def decode_input(self, text, fallback='latin1', default='utf8'):
       	try:
    	    return unicode(text, default)
    	except UnicodeDecodeError:
    	    return unicode(text, fallback)

    def convert(self, text, target):
    	text = self.decode_input(text, self.tunnels[target]['input_fallback'])
        text = text.encode(self.tunnels[target]['output_encoding'], 'ignore')
        return text
    
    def about(self):
        return 'Bridge - Tunnel messages from channel to another plugin'
    
    
def create_plugin(connection, configuration):
    return Bridge(connection, configuration)
