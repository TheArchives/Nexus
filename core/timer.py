# The Nexus software is licensed under the BSD 2-Clause license.
#
# You should have recieved a copy of this license with the software.
# If you did not, you can find one at the following link.
#
# http://opensource.org/licenses/bsd-license.php


import threading, time

class ResettableTimer(threading.Thread):
    """
    The ResettableTimer class is a timer whose counting loop can be reset
    arbitrarily. Its duration is configurable. Commands can be specified
    for both expiration and update. Its update resolution can also be
    specified. Resettable timer keeps counting until the "run" method
    is explicitly killed with the "kill" method.
    """

    def __init__(self, maxtime, inc, expire, update=None):
        """
        @param maxtime: time in seconds before expiration after resetting
                        in seconds
        @param expire: function called when timer expires
        @param inc: amount by which timer increments before
                    updating in seconds, default is maxtime/2
        @param expire: function called when timer completes
        @param update: function called when timer updates
        """
        self.maxtime = maxtime
        self.expire = expire
        self.inc = inc
        if update:
            self.update = update
        else:
            self.update = lambda c : None
        self.counter = 0
        self.stop = False
        threading.Thread.__init__(self)
        self.setDaemon(True)

    def set_counter(self, t):
        """
        Set self.counter to t.
        @param t: new counter value
        """
        self.counter = t

    def kill(self):
        """
        Will stop the counting loop before next update.
        """
        self.stop = True
        self.counter = self.maxtime

    def reset(self):
        """
        Fully rewinds the timer and makes the timer active, such that
        the expire and update commands will be called when appropriate.
        """
        self.counter = 0
        self.stop = False
        
    def run(self):
        """
        Run the timer loop.
        """
        self.counter = 0
        while self.counter < self.maxtime and not self.stop:
            self.counter += self.inc
            time.sleep(self.inc)
            self.update(self.counter)
        if not self.stop:
            self.expire()
