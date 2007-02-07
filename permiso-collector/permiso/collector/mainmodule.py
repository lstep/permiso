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
from twisted.python import threadable
threadable.init()
from twisted.internet import reactor,defer

from twisted.python import failure
from twisted.spread import pb
from twisted.python.util import println
from twisted.python import log
from twisted.application import service
from twisted.cred import credentials

from permiso.collecto import iputils

import sys,os,ConfigParser,Queue
import ipqueue


class ThreadWrapper(object):
    """Wrap an object which presents an asynchronous interface (via Deferreds).

    The wrapped object will present the same interface, but all methods will
    return results, rather than Deferreds.

    This also makes it safe to call non-threadsafe methods from threads
    other than the IO thread.

    This is only useful for wrapping objects accessed by threads other than
    the IO thread.
    """
    def __init__(self, wrappee):
        self.wrappee = wrappee

    def __getattribute__(self, name):
        wrappee = super(ThreadWrapper, self).__getattribute__('wrappee')
        original = getattr(wrappee, name)
        if callable(original):
            return CallableWrapper(original)
        return original

class CallableWrapper(object):
    def __init__(self, original):
        self.original = original
        self.queue = Queue.Queue()

    def __call__(__self, *__a, **__kw):
        reactor.callFromThread(__self.__callFromThread, __a, __kw)
        result = __self.queue.get()
        if isinstance(result, failure.Failure):
            result.raiseException()
        return result

    def __callFromThread(self, a, kw):
        result = defer.maybeDeferred(self.original, *a, **kw)
        result.addBoth(self.queue.put)


class CollectorService(service.Service, pb.Referenceable):
    def __init__(self, *args, **kw):
        self.fmode = 'disconnected'
        self.name = 'CollectorService'
        self.call = None
        self.callR = None
        self.config = None

    def startService(self):
        log.msg('Starting Service CollectorService')
        self.connect_to_identity_service()

    def stopService(self):
        log.msg('Stopping Service CollectorService')
        if self.call:
            self.call.cancel()
    
    def askQ(self, ip_source):
        """ The method that sends a request for information about an ip address """
        if self.fmode == 'connected':
            log.msg('Asking for auth to %s' % ip_source, debug=True)
            
            result = self.callR.callRemote('isAllowed', ip_source)
            log.msg('Auth result for %s is %s' % (ip_source, result), debug=True)
            return result
    
    def connect_to_identity_service(self):
        """ Low level method that connects to the identity server """
        user = self.config.get('main','idservuser')
        password = self.config.get('main','idservpass')

        log.msg('Connecting to the IdServer as user %s...' % user, debug=True)

        self.factory = pb.PBClientFactory()
        reactor.connectTCP(self.config.get('main','idServerIpAddress'),
                           self.config.getint( 'main', 'idServerPort' ),
                           self.factory)
        def1 = self.factory.login(credentials.UsernamePassword(user, password),
                                client=self)
        def1.addCallbacks(callback=self.connected, errback=self.gotError)
        #def1.addCallback(callback=self.actionRequestAuth)
        def1.addErrback(errback=self.genericError)
        
    def connected(self,perspective):
        log.msg("Connected, got perspective ref: %s" % perspective)
        self.fmode = 'connected'
        self.presence = perspective
        self.callR = ThreadWrapper(self.presence)
        self.presence.notifyOnDisconnect(self.got_disconnected)

    def got_disconnected(self,perspective):
        self.fmode = 'disconnected'
        self.presence = None
        log.err('connection - Warning it seems the server has disconnected, will retry in 5 seconds.')
        self.call = reactor.callLater(5, self.connect_to_identity_service)

    def gotError(self, reason):
        log.err("connection - Connection error (will retry in 5 secs): %s" % reason)
        self.presence = None
        self.call = reactor.callLater(5, self.connect_to_identity_service)

    def genericError(self, ref) :
        log.msg("Uncatched error: %s." % ref.getErrorMessage())

class CollectionManager(object):
    """ The network related class that is responsible for getting packets from the IPQUEUE
    queue from the netfilter layer. """
    def __init__(self, cnxPB, config):
        self.cnxPB = cnxPB
        self.config = config
        self.queue = ipqueue.IPQ(ipqueue.IPQ_COPY_PACKET)     #ipqueue.IPQ_COPY_PACKET
        self.running = True
        self.name = "ConnexionMng"
        self.cache = Cache.Cache( timeout=self.config.getint( 'main', 'cacheTime' ),
                            interval=10,
                            name="ConnectionManagerCache" )
        self.cache.start()

    def stop(self):
        log.msg( "Full STOP!" )
        self.running = False
        self.cache.stop()

    def run(self):
        while self.running:
            p = self.queue.read()
            d = iputils.IP(p[ipqueue.PAYLOAD])
            srcIP = d.src_ip()
            dstIP = d.dst_ip()
            proto = d.protocol

            if d.protocol == iputils.SOL_TCP:
                tcp = iputils.TCP(p[ipqueue.PAYLOAD])
                dstPort = tcp.th_dport
            elif d.protocol == iputils.SOL_UDP:
                udp = iputils.UDP(p[ipqueue.PAYLOAD])
                dstPort = udp.th_dport
            else:
                dstPort = 0

            log.msg("proto=%s - ipsrc=%s - ipdst=%s - portdest=%s" % (d.protocol, srcIP, dstIP, dstPort), debug=True)
            result = self.getAuthFor(ipSrc=srcIP)
            if result:
                self.queue.set_verdict(p[0], ipqueue.NF_ACCEPT)
            else:
                log.msg("Refused proto=%s ipsrc=%s ipdest=%s portdest=%s" % (d.protocol, srcIP, dstIP, dstPort))
                self.queue.set_verdict(p[0], ipqueue.NF_DROP)

    def getAuthFor(self,ipSrc):
        if self.cache.isInCache( ipSrc ) :
            #log.msg( 'Already in cache : %s' % ipSrc )
            return self.cache.get( ipSrc )
        else :
            isAllowed = self.cnxPB.askQ(ipSrc)
            #log.debug( 'Not in cache : ', ipSrc )
            if isAllowed:
                self.cache.store( key=ipSrc, data=isAllowed )

            return isAllowed

        





