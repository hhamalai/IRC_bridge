# -*- coding: iso-8859-1 -*-
#!/usr/bin/env python
#
# Dickler IRC Bot
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

import sys
from ircconnection import IRCConnection
from configurationmanager import ConfigurationManager

class Dickler(object):
   
    def __init__(self, configuration):
        self.identity = None
        self.configuration = configuration
        self.connections = set([])
        self.configmanager = ConfigurationManager()
              
    def connect(self):
        if not self.configmanager.read_config(self.configuration):
            return False
            
        for conn in self.configmanager.list_connections():
            c = IRCConnection(conn, self.configmanager.get_identity())
            #for plugin, conf in self.configmanager.list_plugins():
                #c.msg_handler.register_plugin(plugin.create_plugin(c, conf))
            self.connections.add(c)
        
        for conn in self.connections:
            conn.make_connection()
            conn.start()
        
        return True

if __name__ == '__main__':
    configuration = 'settings.py'
    if len(sys.argv) > 1:
        configuration = sys.argv[1]
    dick = Dickler(configuration)
    if not dick.connect():
        logging.warn("Configuration error")
      
    while True:
        input = raw_input()
        if input.strip() == 'quit':
            break
        input = input.split()
        dick.send_local_command(input[0], " ".join(input[1:]))
        
    dick.shutdown()

