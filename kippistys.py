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

from plugin import Plugin
from time import sleep

from threading import Thread
info ='Kippistys 0.1'
kippistys_menossa = None

class KippistysThread(Thread):
    def __init__(self, connection, nick, channel, seconds):
        Thread.__init__(self) 
        self.connection = connection
        self.seconds = seconds
        self.channel = channel

        
        self.connection.send_to("PRIVMSG "+self.channel+" :"+nick+" käynnisti virtuaalikippistyksen. halukkailla on "+str(self.seconds)+" sekuntia aikaa ottaa lasit käteen\n", self.channel)
        self.start()
        
    def run(self):
        while self.seconds > 5:
            sleep(1)
            self.seconds -= 1
        
        while self.seconds > 0:
            self.connection.send_to("PRIVMSG "+self.channel+" :... "+str(self.seconds)+"\n", self.channel)
            self.seconds -= 1
            sleep(1)
            
        self.connection.send_to("PRIVMSG "+self.channel+" :NYT!\n", self.channel)
        global kippistys_menossa
        kippistys_menossa = None
    
    
class Kippistys(Plugin):
    def __init__(self, connection, plugin_config=dict()):
        Plugin.__init__(self, connection)
        self.active_channels = plugin_config.get('channels', [])
        self.commands = {'!kippis': self.do_chanmsg}
           

    def do_chanmsg(self, nick, ident, host, channel, msg):
        global kippistys_menossa
        
        if not channel in self.active_channels:
            return
        
        splitted_msg = msg.split(' ', 2)
        split_length = len(splitted_msg)
        seconds = 10
        
        if split_length > 0:
            if splitted_msg[0] != '!kippis':
                return
            if split_length > 1:
                seconds = splitted_msg[1]
        
        if kippistys_menossa:
            if channel is not None:
                self.connection.send_to("PRIVMSG "+channel+" :valmistautuu kippistämään kanavalla "+kippistys_menossa+"\n")
            else:
                self.connection.send_to("PRIVMSG "+nick+" :valmistautuu kippistämään kanavalla "+kippistys_menossa+"\n")
            return
         
        kippistys_menossa = channel       
    
        try:
            seconds = int(msg[0])
        except:
            seconds = 10

        if seconds > 180:
            seconds = 180
        elif seconds < 0:
            seconds = 10
            
        KippistysThread(self.connection, nick, channel, seconds)
    
    def help(self):
        return 'help: !kippis <seconds>'
    
    def about(self):
        return 'Kippistys - Count timer plugin'
    
    
    
def create_plugin(connection, configuration):
    return Kippistys(connection, configuration)
