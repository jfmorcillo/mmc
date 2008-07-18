#!/usr/bin/python
# -*- coding: utf-8; -*-
#
# (c) 2007-2008 Mandriva, http://www.mandriva.com/
#
# $Id$
#
# This file is part of Pulse 2, http://pulse2.mandriva.org
#
# Pulse 2 is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# Pulse 2 is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Pulse 2; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
# MA 02110-1301, USA.

import logging
import re

from pulse2.proxyssl.utilities import Singleton
import ConfigParser


class Pulse2InventoryProxyConfig(Singleton):
    server = ''
    port = 9999
    local_port = 9999
    path = '/'
    command_name = "C:\Program Files\OCS Inventory Agent\OCSInventory.exe"
    command_attr = "/SERVER:127.0.0.1 /PNUM:9999"
    enablessl = True
    verifypeer = False
    key_file = "conf/key/privkey.pem"
    cert_file = "conf/key/cacert.pem"
    pooling = False
    pooling_time = 600
    flag = ('Software\\Mandriva\\Inventory\\Client', 'do_inventory')
    flag_type = 'reg'

    umask = ''
    daemon_group = 'root'
    daemon_user = 'root'
            

    def setup(self, config_file = 'conf/p2ipc.ini'):
        # Load configuration file
        self.cp = ConfigParser.ConfigParser()
        self.cp.read(config_file)
        self.logger = logging.getLogger()

        if self.cp.has_option('main', 'server'):
            self.server = self.cp.get('main', 'server')
        if self.cp.has_option('main', 'port'):
            self.port = self.cp.getint('main', 'port')
        if self.cp.has_option('main', 'local_port'):
            self.port = self.cp.getint('main', 'local_port')
        if self.cp.has_option('main', 'path'):
            self.path = self.cp.get('main', 'path')
        if self.cp.has_option('main', 'command_name'):
            self.command_name = self.cp.get('main', 'command_name')
        if self.cp.has_option('main', 'command_attr'):
            self.command_attr = self.cp.get('main', 'command_attr').split(' ')
        if self.cp.has_option('main', 'enablessl'):
            self.enablessl = self.cp.getboolean('main', 'enablessl')
        if self.cp.has_option('main', 'verifypeer'):
            self.verifypeer = self.cp.getboolean('main', 'verifypeer')
        if self.cp.has_option('main', 'key_file'):
            self.key_file = self.cp.get('main', 'key_file')
        if self.cp.has_option('main', 'cert_file'):
            self.cert_file = self.cp.get('main', 'cert_file')
        if self.cp.has_option('pooling', 'activate') and self.cp.getboolean('pooling', 'activate'):
            self.pooling = True
            if self.cp.has_option('pooling', 'type') and self.cp.get('pooling', 'type') == 'reg':
                self.flag_type = 'reg'
            else:
                self.logger.error("don't know this type of pooling flag")
                sys.exit(-1)
            if self.cp.has_option('pooling', 'time'):
                self.pooling_time = self.cp.getint('pooling', 'time')
            if self.cp.has_option('pooling', 'path'):
                # TODO if path is given with '/' convert, get the last part to put is as name, remove the begining is HKLM
                path = re.sub("/", "\\\\", self.cp.get('pooling', 'path')).split('\\')
                flag = path.pop()
                if path[0] == 'HKEY_LOCAL_MACHINE':
                    path.reverse()
                    path.pop()
                    path.reverse()
                self.flag = ('\\'.join(path), flag)

