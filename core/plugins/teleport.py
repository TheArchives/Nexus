# The Nexus software is licensed under the BSD 2-Clause license.
#
# You should have recieved a copy of this license with the software.
# If you did not, you can find one at the following link.
#
# http://opensource.org/licenses/bsd-license.php


from ConfigParser import RawConfigParser as ConfigParser
from core.plugins import ProtocolPlugin
from core.decorators import *

class TeleportPlugin(ProtocolPlugin):
    
    commands = {
        "coord": "commandCoord",
        "goto": "commandCoord",
        "tp": "commandTeleport",
        "teleport": "commandTeleport",
        "tpp": "commandTeleProtect",
        "tpo": "commandTeleportOverride",
    }

    @world_list
    def commandCoord(self, parts, fromloc, overriderank):
        "/goto x y z [h p] - Guest\nTeleports you to coords. NOTE: y is up."
        try:
            x = int(parts[1])
            y = int(parts[2])
            z = int(parts[3])
            try:
                try:
                    h = int(parts[4])
                    self.client.teleportTo(x, y, z, h)
                except:
                    p = int(parts[5])
                    self.client.teleportTo(x, y, z, h, p)
            except:
                self.client.teleportTo(x, y, z)
        except (IndexError, ValueError):
            self.client.sendServerMessage("Usage: /goto x y z [h p]")
            self.client.sendServerMessage("MCLawl users: /l world name")

    @mod_only
    def commandTeleProtect(self, parts, fromloc, overriderank):
        "/tpp on|off - Mod\nEngages TeleProtection for yourself."
        if len(parts) != 2:
            self.client.sendServerMessage("You must specify either \'on\' or \'off\'.")
        elif parts[1] == "on":
            config = ConfigParser()
            config.read('config/data/tpprot.meta')
            config.add_section(self.client.username)
            fp = open('config/data/tpprot.meta', "w")
            config.write(fp)
            fp.close()
            self.client.sendServerMessage("Teleport protection is now on.")
        elif parts[1] == "off":
            config = ConfigParser()
            config.read('config/data/tpprot.meta')
            config.remove_section(self.client.username)
            fp = open('config/data/tpprot.meta', "w")
            config.write(fp)
            fp.close()
            self.client.sendServerMessage("Teleport protection is now off.")
        else:
            self.client.sendServerMessage("You must specify either \'on\' or \'off\'.")
            
    def doTeleportToUser(self, user):
        x = user.x >> 5
        y = user.y >> 5
        z = user.z >> 5
        if user.world == self.client.world:
            self.client.teleportTo(x, y, z)
        else:
            if (self.client.canEnter(user.world)):
                self.client.changeToWorld(user.world.id, position=(x, y, z))
            else:
                self.client.sendServerMessage(self.client.getReasonCannotEnter(user.world))
    
    @player_list
    @username_command
    @admin_only
    def commandTeleportOverride(self, user, fromloc, overriderank):
        "/tp username - Guest\nAliases: teleport\nTeleports you to the users location."
        self.doTeleportToUser(user)


    @player_list
    @username_command
    def commandTeleport(self, user, fromloc, overriderank):
        "/tp username - Guest\nAliases: teleport\nTeleports you to the users location."
        x = user.x >> 5
        y = user.y >> 5
        z = user.z >> 5
        if self.client.isDirector() or self.client.isServerOwner():
            self.doTeleportToUser(user)
        else:
            config = ConfigParser()
            config.read('config/data/tpprot.meta')
            if config.has_section(user.username):
                self.client.sendServerMessage("You can't tp to this person; they're TeleProtected!")
            else:
                self.doTeleportToUser(user)
