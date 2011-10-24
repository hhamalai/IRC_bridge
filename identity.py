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

import types

class Identity(object):
    def __init__(self):
        self.nick = "Dickler"
        self.realname = "Anonymous No Name"
        self.secret = None
        
    def load_identity(self, target):
        if not target.has_key('nick') or not target.has_key('realname'):
            return False

        if type(target['nick']) != types.StringType:
            return False
        self.nick = target['nick']
        
        if type(target['realname']) != types.StringType:
            return False
        self.realname = target['realname']
        
        if target.has_key('secret'):
            if type(target['secret']) != types.StringType:
                return False
            self.secret = target.secret
            
        return True
        
