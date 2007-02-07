# -*- coding: utf-8 -*-
"""
Copyright (C) 2007 Adelux <contact@adelux.fr>

This program is free software; you can redistribute it and/or
modify it under the terms of the GNU General Public License
as published by the Free Software Foundation; either version 2
of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program; if not, write to the Free Software
Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.
"""
from twisted.application import service
from twisted.internet import reactor, defer, task
from twisted.python import log

class CollectorService(service.Service):
    def __init__(self):
        self.QQueue = []
        self.verify_expired_process = task.LoopingCall(self.verify_expired)

    def startService(self):
        log.msg('Starting Service')
        # Removes every 10 seconds all the stale entries in the queue
        self.verify_expired_process.start(10)
        service.Service.startService(self)

    def stopService(self):
        log.msg('Stopping Service')
        self.verify_expired_process.stop()
        service.Service.stopService(self)

    #####

    def verify_expired(self):
        log.msg('verifying...')


