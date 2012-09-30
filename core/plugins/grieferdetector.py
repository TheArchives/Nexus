# The Nexus software is licensed under the BSD 2-Clause license.
#
# You should have recieved a copy of this license with the software.
# If you did not, you can find one at the following link.
#
# http://opensource.org/licenses/bsd-license.php


import logging, datetime
from core.plugins import ProtocolPlugin
from core.decorators import *
from core.constants import *
from reqs.twisted.internet import reactor

class GreiferDetectorPlugin(ProtocolPlugin):

    hooks = {
        "blockchange": "blockChanged",
        "newworld": "newWorld",
    }
    
    def gotClient(self):
        self.var_blockchcount = 0
        self.in_publicworld = False
    
    def blockChanged(self, x, y, z, block, selected_block, fromloc):
        "Hook trigger for block changes."
        world = self.client.world
        if block is BLOCK_AIR and self.in_publicworld:
            if ord(world.blockstore.raw_blocks[world.blockstore.get_offset(x, y, z)]) != 3:
                worldname = world.id
                username = self.client.username
                def griefcheck():
                    if self.var_blockchcount >= self.client.factory.grief_blocks:
                        self.client.factory.queue.put((self.client, TASK_STAFFMESSAGE, ("#%s%s: %s%s" % (COLOUR_DARKGREEN, 'Console ALERT', COLOUR_DARKRED, "Possible grief behavior was detected;", False))))
                        self.client.factory.queue.put((self.client, TASK_STAFFMESSAGE, ("#%s%s: %s%s" % (COLOUR_DARKGREEN, 'Console ALERT', COLOUR_DARKRED, "World: "+worldname+" | User: "+username, False))))
                        self.client.logger.warning("%s was detected as a possible griefer in world %s." % (username, worldname))
                        self.client.adlog.write(datetime.datetime.utcnow().strftime("%Y/%m/%d %H:%M:%S")+" | #Console ALERT: Possible grief behavior was detected; World: "+worldname+" | User: "+username+"\n")
                        self.client.adlog.flush()
                    self.var_blockchcount = 0
                if self.var_blockchcount == 0:
                    reactor.callLater(self.client.factory.grief_time, griefcheck)
                self.var_blockchcount += 1
                
    def newWorld(self, world):
        "Hook to reset portal abilities in new worlds if not op."
        if world.id.find('public') == -1:
            self.in_publicworld = False
            self.var_blockchcount = 0
        else:
            self.in_publicworld = True
