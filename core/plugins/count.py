# The Nexus software is licensed under the BSD 2-Clause license.
#
# You should have recieved a copy of this license with the software.
# If you did not, you can find one at the following link.
#
# http://opensource.org/licenses/bsd-license.php


from core.plugins import ProtocolPlugin
from core.decorators import *
from core.constants import *
from core.timer import ResettableTimer

class CountPlugin(ProtocolPlugin):
    
    commands = {
        "count": "commandCount",
        "countdown": "commandCount",
    }

    def gotClient(self):
        self.num = int(0)

    @op_only
    def commandCount(self, parts, fromloc, overriderank):
        "/count [number] - Op\nAliases: countdown\nCounts down from 3 or from number given (up to 15)"
        if self.num != 0:
            self.client.sendServerMessage("You can only have one count at a time!")
            return
        if len(parts) > 1:
            try:
                self.num = int(parts[1])
            except ValueError:
                self.client.sendServerMessage("Number must be an integer!")
                return
        else:
            self.num = 3
        if self.num > 15:
            self.client.sendServerMessage("You can't count from higher than 15!")
            self.num = 0
            return
        counttimer = ResettableTimer(self.num, 1, self.sendgo, self.sendcount)
        self.client.sendPlainWorldMessage("&7COUNTDOWN: &c%s" %self.num)
        counttimer.start()

    def sendgo(self):
        self.client.sendPlainWorldMessage("&7GET SET: &aGO!")
        self.num = 0

    def sendcount(self, count):
        if int(self.num)-int(count) == 1:
            self.client.sendPlainWorldMessage("&7GET READY: &e1")
        elif not int(self.num)-int(count) == 0:
            self.client.sendPlainWorldMessage("&7COUNTDOWN: &c%s" %(int(self.num)-int(count)))
