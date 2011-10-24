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

import unittest

from identity import Identity
from ircconnection import IRCConnection
from commandparser import CommandParser
from configurationmanager import ConfigurationManager
from messagehandler import MessageHandler
from plugin import Plugin
from kippistys import Kippistys


class TestCommandParser(unittest.TestCase):
    def setUp(self):
        self.cp = CommandParser()
        
    def testSayCommand(self):
        self.assertEqual('PRIVMS #dickler :hello to everyone', self.cp.parse('say #dickler hello to everyone'))

        
class TestConfigurationManager(unittest.TestCase):
    def setUp(self):
        self.cm = ConfigurationManager()
    
    def testReadConnections(self):
        self.cm.read_config('settings-test.py')
        self.assertEquals(len(self.cm.list_connections()), 2)
        for conn in self.cm.list_connections():
            assert(conn.has_key('endpoint'))
            assert(conn.has_key('channels'))
            

class TestMessageHandler(unittest.TestCase):
    def setUp(self):
        self.conn = IRCConnection({'endpoint': ("192.168.1.10", 6667), 'channels': ['#foo']}, Identity(), debug=True)
        
        self.conn.msg_handler.plugins.append(Plugin(self.conn))
        self.conn.msg_handler.plugins.append(Kippistys(self.conn))
        self.assertEqual(2, len(self.conn.msg_handler.plugins))
        
    def testRegisterPlugin(self):
        self.conn.msg_handler.unregister_plugins()
        self.assertEqual(0, len(self.conn.msg_handler.plugins))
        self.conn.msg_handler.plugins.append(Plugin(self.conn))
        self.conn.msg_handler.plugins.append(Kippistys(self.conn))
        self.assertEqual(2, len(self.conn.msg_handler.plugins))
        
    def testKick(self):
        type, matched_plugins = self.conn.msg_handler.message(':foo@bar KICK #foo bar :baz')
        self.assertEqual(type, 'kick')
        self.assertEqual(matched_plugins, 0)
    
    def testPart(self):
        type, matched_plugins = self.conn.msg_handler.message(':foo@bar PART #foo :baz')
        self.assertEqual(type, 'part')
        self.assertEqual(matched_plugins, 0)
    
    def testQuit(self):
        type, matched_plugins = self.conn.msg_handler.message(':foo@bar QUIT :baz')
        self.assertEqual(type, 'quit')
        assert(matched_plugins, 0)
        
    def testChannelMessage(self):
        type, matched_plugins = self.conn.msg_handler.message(':foo@bar PRIVMSG #foobar :baz')
        self.assertEqual(type, 'chanmsg')
        self.assertEqual(matched_plugins, 1)
        
    def testPrivateMessage(self):
        type, matched_plugins = self.conn.msg_handler.message(':foo@bar PRIVMSG foobar :baz')
  

def main():
    unittest.main()
    #suite = unittest.TestLoader().loadTestsFromTestCase(TestConfigurationManager)
    #unittest.TextTestRunner(verbosity=2).run(suite)
            
if __name__ == '__main__':
    main()