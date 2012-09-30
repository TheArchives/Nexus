# The Nexus software is licensed under the BSD 2-Clause license.
#
# You should have recieved a copy of this license with the software.
# If you did not, you can find one at the following link.
#
# http://opensource.org/licenses/bsd-license.php


from core.plugins import ProtocolPlugin
from core.decorators import *
from core.constants import *
from reqs.twisted.internet import reactor

class LavaPlugin(ProtocolPlugin):

    hooks = {
        "poschange": "posChanged",
    }

    def gotClient(self):
        self.died = False

    def posChanged(self, x, y, z, h, p):
        "Hook trigger for when the user moves"
        rx = x >> 5
        ry = y >> 5
        rz = z >> 5
        if hasattr(self.client.world.blockstore, "raw_blocks"):
            try: 
                check_offset = self.client.world.blockstore.get_offset(rx, ry, rz)
                try:
                    block = self.client.world.blockstore.raw_blocks[check_offset]
                except (IndexError):
                    return
                check_offset = self.client.world.blockstore.get_offset(rx, ry-1, rz)
                blockbelow = self.client.world.blockstore.raw_blocks[check_offset]
            except (KeyError, AssertionError):
                pass
            else:
                if block == chr(BLOCK_LAVA) or blockbelow == chr(BLOCK_LAVA):
                #or block == chr(BLOCK_STILLLAVA) or blockbelow == chr(BLOCK_STILLLAVA):
                    # Ok, so they touched lava. Warp them to the spawn, timer to stop spam.
                    if self.died is False:
                        self.died = True
                        self.client.teleportTo(self.client.world.spawn[0], self.client.world.spawn[1], self.client.world.spawn[2], self.client.world.spawn[3])
                        self.client.factory.queue.put ((self.client.world,TASK_WORLDMESSAGE, (255, self.client.world, COLOUR_DARKRED+self.client.username+" has died from lava.")))
                        reactor.callLater(1, self.unDie)
                        
    def unDie(self):
        self.died = False
