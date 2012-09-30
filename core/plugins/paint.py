# The Nexus software is licensed under the BSD 2-Clause license.
#
# You should have recieved a copy of this license with the software.
# If you did not, you can find one at the following link.
#
# http://opensource.org/licenses/bsd-license.php


from core.plugins import ProtocolPlugin
from core.decorators import *
from core.constants import *

class PaintPlugin(ProtocolPlugin):
    
    commands = {
        "paint": "commandPaint",
    }
    
    hooks = {
        "preblockchange": "blockChanged",
    }
    
    def gotClient(self):
        self.painting = False
    
    def blockChanged(self, x, y, z, block, selected_block, fromloc):
        "Hook trigger for block changes."
        if block is BLOCK_AIR and self.painting:
            return selected_block
    
    @build_list
    def commandPaint(self, parts, fromloc, overriderank):
        "/paint - Guest\nLets you break-and-build in one move. Toggle."
        if self.painting:
            self.painting = False
            self.client.sendServerMessage("Painting mode is now off.")
        else:
            self.painting = True
            self.client.sendServerMessage("Painting mode is now on.")
