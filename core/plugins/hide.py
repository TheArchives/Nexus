# The Nexus software is licensed under the BSD 2-Clause license.
#
# You should have recieved a copy of this license with the software.
# If you did not, you can find one at the following link.
#
# http://opensource.org/licenses/bsd-license.php


import random
from core.plugins import ProtocolPlugin
from core.decorators import *
from core.constants import *

class HidePlugin(ProtocolPlugin):
    
    commands = {
        "hide": "commandHide",
        "cloak": "commandHide",
    }
    
    hooks = {
        "playerpos": "playerMoved",
    }
    
    def gotClient(self):
        self.hidden = False
    
    def playerMoved(self, x, y, z, h, p):
        "Stops transmission of user positions if hide is on."
        if self.hidden:
            return False
    
    @player_list
    @op_only
    def commandHide(self, params, fromloc, overriderank):
        "/hide - Op\nAliases: cloak\nHides you so no other users can see you. Toggle."
        if not self.hidden:
            self.client.sendServerMessage("You have vanished.")
            self.hidden = True
            # Send the "user has disconnected" command to people
            self.client.queueTask(TASK_PLAYERLEAVE, [self.client.id])
        else:
            self.client.sendServerMessage("That was Magic!")
            self.hidden = False
            # Imagine that! They've mysteriously appeared.
            self.client.queueTask(TASK_NEWPLAYER, [self.client.id, self.client.username, self.client.x, self.client.y, self.client.z, self.client.h, self.client.p])
