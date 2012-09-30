# The Nexus software is licensed under the BSD 2-Clause license.
#
# You should have recieved a copy of this license with the software.
# If you did not, you can find one at the following link.
#
# http://opensource.org/licenses/bsd-license.php


from core.plugins import ProtocolPlugin
from core.decorators import *

class SpectatePlugin(ProtocolPlugin):
    
    commands = {
        "spectate": "commandSpectate",
        "follow": "commandSpectate",
        "watch": "commandSpectate",
        "possess": "commandPossess",
    }
    
    hooks = {
        "poschange": "posChanged",
    }
    
    def gotClient(self):
        self.flying = False
        self.last_flying_block = None
    
    def posChanged(self, x, y, z, h, p):
        "Hook trigger for when the user moves"

        spectators = set()

        for uid in self.client.factory.clients:
            user = self.client.factory.clients[uid]

            try:
                if user.spectating == self.client.id:
                    if user.x != x or user.y != y or user.z != z:
                        user.teleportTo(x >> 5, y >> 5, z >> 5, h, p)
            except AttributeError:
                pass
            try:
               if self.client.possessing == user.id:
                    if user.x != x or user.y != y or user.z != z:
                        user.teleportTo(x >> 5, y >> 5, z >> 5, h, p)
            except AttributeError:
                pass
   
    @player_list
    @op_only
    @username_command
    def commandSpectate(self, user, fromloc, overriderank):
        "/spectate username - Guest\nAliases: follow, watch\nFollows specified user around"

        nospec_check = True

        try:
            self.client.spectating
        except AttributeError:
            nospec_check = False

        if not nospec_check or self.client.spectating != user.id:
            self.client.sendServerMessage("You are now spectating %s" % user.username)
            self.client.spectating = user.id
        else:
            self.client.sendServerMessage("You are no longer spectating %s" % user.username)
            self.client.spectating = False

    @player_list
    @director_only
    @username_command
    def commandPossess(self, user, fromloc, overriderank):
        "/possess username - Admin\nControls the specified user"

        nopossess_check = True

        try:
            self.client.possessing
        except AttributeError:
            nopossess_check = False

        if not nopossess_check or self.client.possessing != user.id:
            self.client.sendServerMessage("You are now possessing %s." % user.username)
            self.client.possessing = user.id
        else:
            self.client.sendServerMessage("You are no longer possessing %s." % user.username)
            self.client.possessing = False

