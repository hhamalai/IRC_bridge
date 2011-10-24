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

from identity import Identity

class ConfigurationManager(object):
    
    def read_config(self, path):
        path = path.split('.').pop(0).split('/').pop()
        confmod = __import__(path)
        self.identity = Identity()
        if not self.identity.load_identity(confmod.conf['identity']):
            return False
        
        self.connections = []
        
        for connection in confmod.conf['connections']:
            plugins = []
            # XXX Validate existance of connections.plugins
            for plugin_config in connection.get('plugins', []):
                if not plugin_config.get('module'):
                    continue
                filename = plugin_config['module']
                try:
                    name = filename.rsplit('.')[0]
                except (IndexError, ValueError):
                    logging.warn('Invalid module filename \'%s\'' % filename)
                else:
                    module = __import__(name)
                    plugins.append((module, plugin_config))

            connection['plugins'] = plugins
            self.connections.append(connection)
        return True
        
    def get_identity(self):
        return self.identity
    
    def list_connections(self):
        return self.connections
    
