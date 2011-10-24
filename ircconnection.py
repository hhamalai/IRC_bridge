# -*- coding: iso-8859-1 -*-
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
import socket
import select
import time

from threading import Thread
from identity import Identity
from messagehandler import MessageHandler

class IRCConnection(Thread):
    def __init__(self, connection, identity, debug=False):
        Thread.__init__(self)
        self.setDaemon(True)
        self.end_point = connection.get('endpoint', None)
        self.channels = connection.get('channels', ()) 
        self.plugins = connection.get('plugins', [])
        self.chatters = {}
        self.msg_handler = MessageHandler(self)
        self.identity = identity
        self.active = False
        self.plugins_loaded = False
        self.updating_chatters = False
        self.debug = debug                
    
    def init_plugins(self):
        for plugin in self.plugins:
            # plugin is a (module, config) -tuple
            self.msg_handler.register_plugin(plugin[0].create_plugin(self, plugin[1]))

    def get_nick(self):
        return self.identity.nick
                   
    def make_connection(self):
        if not self.end_point:
            logging.warn('Endpoint does not exists')
            return False
        
        connection_ok = False
            
        if self.debug:
            logging.info("making connection in debug mode")
            return
        
        self.msg_handler.prepare_handler()
        self.active = True

        while not connection_ok:
            logging.warn("Connecting to %s:%s" % (self.end_point[0], self.end_point[1]))
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.settimeout(1)
            try:
                self.socket.connect((self.end_point[0], self.end_point[1]))
                connection_ok = True
                break
            except socket.gaierror:
                continue
            except socket.timeout:
                continue
            except:
                logging.info("Connection refused, waiting a couple seconds before reconnecting")
                time.sleep(30)
                continue
    
        self.input = self.socket.makefile('rb', 0)
        self.output = self.socket.makefile('wb', 0)
        
        self.output.write('NICK %s \n' % self.identity.nick)
        self.output.write('USER %s 0 0 : %s \n' % (self.identity.nick, self.identity.realname))

        if self.plugins_loaded == False:
            self.init_plugins()
            self.plugins_loaded = True
        
        for channel in self.channels:
           self.chatters[channel] = set([])
           self.output.write('JOIN %s \n' % channel)
        
        self.active = True
        

    def run(self):
        while self.active:
            to_read, ignore, ignore = select.select([self.input], [], [], 360)
            if len(to_read) == 0:
                self.active = False
                self.make_connection()
            else:
                for input in to_read:
                    input_text = self.input.readline()
                    if input_text:
                        self.msg_handler.message(input_text)
                    else:
                        logging.warn("Connection lost to %s" % self.end_point[0])
                        self.active = False
                        self.make_connection()


    def update_messagehandler(self, plugins):
        self.msg_handler.unregister_plugins()
        for plugin in plugins:
            self.msg_handler.register_plugin(plugin)


    def send_to(self, output_text, channel=""):
        if self.debug:
            logging.warn("Pushing message to pipe: %s" % output_text)
        
        self.msg_handler.process_output(output_text, channel)
        self.output.write(output_text)

    def update_chatters(self, channel, nicklist):
        if not self.updating_chatters:
            self.chatters[channel] = set(nicklist)
        else:
            self.chatters[channel].add(nicklist)
        self.updating_chatters = True

    def update_chatters_ready(self):
        self.updating_chatters = False

    def change_chatter(self, nick, newnick):
        for chan in self.chatters.keys():
            if nick in self.chatters[chan]:
                self.chatters[chan].remove(nick)
                self.chatters[chan].add(newnick)

    def add_chatter(self, channel, nick):
        self.chatters[channel].add(nick)

    def remove_chatter(self, channel, nick):
        if nick in self.chatters[channel]:
            self.chatters[channel].remove(nick)

    def fully_remove_chatter(self, nick):
        for channel in self.chatters.keys():
            self.chatters[channel].discard(nick)

