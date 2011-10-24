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

info = 'Generic plugin'

class Plugin(object):
    def __init__(self, connection, configuration=None):
        # Server connection associated with this plugin
        self.connection = connection
        # Methods provided by this plugin
        self.commands = {'foo': self.bar}
    
    # Plugin specific methods
    def bar(self, nick, ident, host, channel, msg):
        self.connection.send_to("PRIVMSG "+channel+" :bar\n")
    
    # Event based methods
    # def on_join(self, nick, ident, host, channel):
    #    print "on_join"
    
    # Generic methods required by each plugin
    def help(self):
        return "No help available"
    
    def about(self):
        return "Generic plugin example"
    
def create_plugin(connection, configuration):
    return Plugin(connection, configuration)
