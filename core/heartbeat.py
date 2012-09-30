import logging, time, traceback, threading, urllib, urllib2

from reqs.twisted.internet import reactor

from core.constants import *

class Heartbeat(object):
    """
    Deals with registering with the Minecraft main server every so often.
    The Salt is also used to help verify users' identities.
    """

    def __init__(self, factory):
        self.factory = factory
        self.logger = logging.getLogger("Heartbeat")
        self.turl()

    def turl(self):
        #self.logger.info("Main Thread ID = %s" % threading.currentThread().ident)      # for debugging purposes
        try:
            hbThread = threading.Thread(target=self.threadFunc)
            hbThread.daemon = True      # don't let this thread cause shutting down to hang 
            hbThread.start()
        except:
            self.logger.error(traceback.format_exc())
            reactor.callLater(1, self.turl)

    def get_url(self, noisy=False):
        #self.logger.info("HB Thread ID = %s" % threading.currentThread().ident)      # for debugging purposes
        try:
            self.factory.last_heartbeat = time.time()
            
            data = urllib.urlencode({
            "port": self.factory.server_port,
            "max": self.factory.max_clients,
            "name": self.factory.server_name,
            "public": self.factory.public,
            "version": 7,
            "salt": self.factory.salt,
            "users": len(self.factory.clients),
            })
            print data
            fh = urllib2.urlopen(self.factory.heartbeat_url, urllib.urlencode({
            "port": self.factory.server_port,
            "max": self.factory.max_clients,
            "name": self.factory.server_name,
            "public": self.factory.public,
            "version": 7,
            "salt": self.factory.salt,
            "users": len(self.factory.clients),
            }), 30)
            self.url = fh.read().strip()
            if noisy:
                self.logger.info("Heartbeat Sent. Your URL (saved to docs/SERVERURL): %s" % self.url)
            else:
                self.logger.debug("Heartbeat Sent. Your URL (saved to docs/SERVERURL): %s" % self.url)
            open('config/data/SERVERURL', 'w').write(self.url)
            print self.url
            
            if self.factory.use_second_heartbeat:
                fh = urllib2.urlopen(self.factory.heartbeat_url, urllib.urlencode({
                "port": self.factory.server_port2,
                "max": self.factory.max_clients,
                "name": self.factory.server_name2,
                "public": self.factory.public,
                "version": 7,
                "salt": self.factory.salt,
                "users": len(self.factory.clients),
                }), 30)
                self.url2 = fh.read().strip()
                if noisy:
                    self.logger.info("Heartbeat Sent. Your alternative URL (saved to docs/SERVERURL2): %s" % self.url2)
                else:
                    self.logger.debug("Heartbeat Sent. Your alternative URL (saved to docs/SERVERURL2): %s" % self.url2)
                open('config/data/SERVERURL2', 'w').write(self.url)
            
            if not self.factory.console.is_alive():
                self.factory.console.run()
        except urllib2.URLError as r:
            self.logger.error("Minecraft.net seems to be offline: %s" % r)
        except:
            self.logger.error(traceback.format_exc())
                
    def threadFunc(self):
        while True:
            self.get_url()
            time.sleep(60)
