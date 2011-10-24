# -*- coding: iso-8859-1 -*-
#
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

import logging
import re

def parse_nicks(s):
    r = re.compile(r'[A-aZ-z0-9\-\[\]\|\\\`\^\{\}]+')
    return r.findall(s)

class MessageHandler(object):
    ping_pattern = re.compile(r'(^PING (.*))')
    kick_pattern = re.compile(r':([^!]*)!?([^@]*)@?(.*) KICK ([#!]+.*) (.*) :(.*)')
    nick_pattern = re.compile(r':([^!]*)!?([^@]*)@?(.*) NICK :(.*)')
    action_pattern = re.compile(r':([^!]*)!?([^@]*)@(.+) PRIVMSG ([#!]\S+) :[\x01]ACTION (.+)[\x01]')
    chanmsg_pattern = re.compile(r':([^!]*)!?([^@]*)@(.+) PRIVMSG ([#!]\S+) :(.+)')
    quit_pattern = re.compile(r':([^!]*)!?([^@]*)@?(.*) QUIT :(.*)')
    privmsg_pattern = re.compile(r':([^!]*)!?([^@]*)@(.*) PRIVMSG ([A-Za-z0-9^-_]+) :(.+)')
    join_pattern = re.compile(r':([^!]*)!?([^@]*)@?(.*) JOIN :(.*)')
    topic_pattern = re.compile(r':([^!]*)!?([^@]*)@?(.*) TOPIC ([#!]+.*) :(.*)')
    part_pattern = re.compile(r':([^!]*)!?([^@]*)@?(.*) PART ([#!]+.*) :(.*)')
    quit_pattern = re.compile(r':([^!]*)!?([^@]*)@?(.*) QUIT :(.*)')
    names_begin_pattern = None#re.compile(r':(\S*) 353 (%s) = ([#!]+.*) :(.*)' % get_identity().nick)
    names_end_pattern = None#re.compile(r':(\S*) 366 (%s) ([#!]+.*) :(.*)' % get_identity().nick)
       
    def __init__(self, connection):    
        self.connection = connection
        self.plugins = []

    
    def register_plugin(self, plugin):
        logging.warn("Plugin config %s " % plugin.about())
        self.plugins.append(plugin)
    
    def prepare_handler(self):
        self.names_begin_pattern = re.compile(r':(\S*) 353 (%s) = ([#!]+.*) :(.*)' % self.connection.get_nick())
        self.names_end_pattern = re.compile(r':(\S*) 366 (%s) ([#!]+.*) :(.*)' %  self.connection.get_nick())


    def unregister_plugin(self, target):
        for plugin in self.plugins:
            if plugin == target:
                self.plugins.remove(target)
                return True
        return False

    def unregister_plugins(self):
        self.plugins = []
        
    
    def message_ping(self, match):
        self.connection.send_to("PONG "+match.group(2))
        
        plugins_matched = 0
        
        for plugin in self.plugins:
            if hasattr(plugin, 'do_ping'):
                plugins_matched += 1
                plugin.do_ping()
        
        return plugins_matched
            
        
    def message_kick(self, match):
        kicker = match.group(1)
        ident = match.group(2)
        host = match.group(3)
        channel = match.group(4).lower()
        nick = match.group(5).lower()
        msg = match.group(6).strip()
        
        plugins_matched = 0
        
        for plugin in self.plugins:
            if hasattr(plugin, 'do_kick'):
                plugins_matched += 1
                plugin.do_kick(kicker, ident, host, channel, nick, msg)
        
        self.connection.remove_chatter(channel, nick)       
        return plugins_matched
            
    def message_quit(self, match):
        nick = match.group(1)
        ident = match.group(2)
        host = match.group(3)
        quitmsg = match.group(4).strip()
        
        plugins_matched = 0
        
        for plugin in self.plugins:
            if hasattr(plugin, 'do_quit'):
                plugins_matched += 1
                plugin.do_quit(nick, ident, host, quitmsg)

        self.connection.fully_remove_chatter(nick)       
        return plugins_matched
            
    
    def message_names(self, match):
        channel = match.group(1)
        names = match.group(2)
        
        plugins_matched = 0
        
        for plugin in self.plugins:
            if hasattr(plugin, 'do_names'):
                plugins_matched += 1
                plugin.do_names(channel, names)
        
        return plugins_matched
        
            
    def message_nick(self, match):
        nick = match.group(1)
        ident = match.group(2)
        host = match.group(3)
        new_nick = match.group(4).strip()
        
        plugins_matched = 0
        for plugin in self.plugins:
            if hasattr(plugin, 'do_nick'):
                plugins_matched += 1
                plugin.do_nick(nick, ident, host, new_nick)

        self.connection.change_chatter(nick, new_nick)       
        return plugins_matched
    
    def message_action(self, match):
        nick = match.group(1)
        ident = match.group(2)
        host = match.group(3)
        channel = match.group(4).lower()
        msg = match.group(5).strip()
        
        plugins_matched = 0

        for plugin in self.plugins:

            if hasattr(plugin, 'do_action'):
                plugins_matched += 1
                plugin.do_action(nick, ident, host, channel, msg)
            
        return plugins_matched
 

            
    def message_chanmsg(self, match):
        nick = match.group(1)
        ident = match.group(2)
        host = match.group(3)
        channel = match.group(4).lower()
        msg = match.group(5).strip()
        
        plugins_matched = 0

        for plugin in self.plugins:

            if hasattr(plugin, 'do_chanmsg'):
                plugins_matched += 1
                plugin.do_chanmsg(nick, ident, host, channel, msg)
            
        return plugins_matched
 
    def message_priv(self, match):
        nick = match.group(1)
        ident = match.group(2)
        host = match.group(3)
        msg = match.group(4).strip()
 
        plugins_matched = 0
        
        for plugin in self.plugins:
            if hasattr(plugin, 'do_privmsg'):
                plugins_matched += 1
                plugin.do_privmsg(nick, ident,  host, msg)
        
        return plugins_matched
 
    def message_topic(self, match):
        nick = match.group(1)
        ident = match.group(2)
        host = match.group(3)
        channel = match.group(4).strip().lower()
        topic = match.group(5).strip()
        
        plugins_matched = 0
        
        for plugin in self.plugins:
            if hasattr(plugin, 'do_topic'):
                plugins_matched += 1
                plugin.do_topic(nick, ident, host, channel, topic)
        
        return plugins_matched
        
    def message_join(self, match):
        nick = match.group(1)
        if nick == self.connection.identity.nick:
            return
        ident = match.group(2)
        host = match.group(3)
        channel = match.group(4).strip().lower()
        
        plugins_matched = 0
        
        for plugin in self.plugins:
            if hasattr(plugin, 'do_join'):
                plugins_matched += 1
                plugin.do_join(nick, ident, host, channel)

        self.connection.add_chatter(channel, nick)
        return plugins_matched
        
    def message_part(self, match):
        nick = match.group(1)
        ident = match.group(2)
        host = match.group(3)
        channel = match.group(4).strip().lower()
        msg = match.group(5).strip()
        
        plugins_matched = 0
        
        for plugin in self.plugins:
            if hasattr(plugin, 'do_part'):
                plugins_matched += 1
                plugin.do_part(nick, ident, host, channel, msg)

        self.connection.remove_chatter(channel, nick)
        return plugins_matched
    
    def message_namesbegin(self, match):
        server = match.group(1)
        nick = match.group(2)
        channel = match.group(3)
        nicklist = match.group(4)
        assert server and nick and channel and nicklist
        self.connection.update_chatters(channel, parse_nicks(nicklist))
        return 0

    def message_namesend(self, match):
        server = match.group(1)
        nick = match.group(2)
        channel = match.group(3)
        reason = match.group(4)
        assert server and nick and channel
        self.connection.update_chatters_ready()
        return 0

    def message(self, message):
        match = self.ping_pattern.match(message)      
        if match:
            return ('ping', self.message_ping(match))
            
        match = self.quit_pattern.match(message)
        if match:
            return ('quit', self.message_quit(match))
                          
        match = self.nick_pattern.match(message)
        if match:
            return ('nick', self.message_nick(match))
            
        match = self.part_pattern.match(message)
        if match:
            return ('part', self.message_part(match))
        
        match = self.action_pattern.match(message)
        if match:
            return ('action', self.message_action(match))   
        
        match = self.chanmsg_pattern.match(message)
        if match:
            return ('chanmsg', self.message_chanmsg(match))
            
        match = self.privmsg_pattern.match(message)
        if match:
            return ('privmsg', self.message_priv(match))
            
        match = self.join_pattern.match(message)
        if match:
            return ('join', self.message_join(match))
            
        match = self.kick_pattern.match(message)
        if match:
            return ('kick', self.message_kick(match))
        
        match = self.topic_pattern.match(message)
        if match:
            return ('topic', self.message_topic(match))
        
        match = self.names_begin_pattern.match(message)
        if match:
            return ('namesbegin', self.message_namesbegin(match))
        
        match = self.names_end_pattern.match(message)
        if match:
            return ('namesend', self.message_namesend(match))

    def process_output(self, message, channel):
        for plugin in self.plugins:
            if hasattr(plugin, "do_output"):
                plugin.do_output(message, channel)
