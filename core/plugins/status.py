# The Nexus software is licensed under the BSD 2-Clause license.
#
# You should have recieved a copy of this license with the software.
# If you did not, you can find one at the following link.
#
# http://opensource.org/licenses/bsd-license.php


from core.plugins import ProtocolPlugin
from core.decorators import *
from core.constants import *

class WorldUtilPlugin(ProtocolPlugin):
    
    commands = {
        "status": "commandStatus",
        "mapinfo": "commandStatus",
        "setspawn": "commandSetspawn",
        "setowner": "commandSetOwner",
        "owner": "commandSetOwner",
        "worldowner": "commandSetOwner",
        "where": "commandWhere",
        "ops": "commandOps",
        "writers": "commandBuilders",
        "builders": "commandBuilders",
    }

    @player_list
    @mod_only
    def commandSetOwner(self, parts, fromloc, overriderank):
        "/setowner [username] - Mod\nAliases: owner, worldowner\nSets the world's owner string, or unsets it."
        old_owner = self.client.world.owner
        if len(parts) == 1:
            self.client.world.owner = "N/A"
            self.client.sendServerMessage("The World Owner has been unset.")
        else:
            self.client.world.owner = str(parts[1].lower())
            self.client.sendServerMessage("The World Owner has been set to %s." % self.client.world.owner)
        self.client.factory.updateWorldOwnerIndex(self.client.world.id, old_owner, self.client.world.owner)

    @info_list
    def commandOps(self, parts, fromloc, overriderank):
        "/ops - Guest\nLists this world's ops"
        if not self.client.world.ops:
            self.client.sendServerMessage("This world has no Ops.")
        else:
            self.client.sendServerList(["Ops for %s:" % self.client.world.id] + list(self.client.world.ops))

    @info_list
    def commandBuilders(self, parts, fromloc, overriderank):
        "/builders - Guest\nAliases: writers\nLists this world's builders."
        if not self.client.world.builders:
            self.client.sendServerMessage("This world has no builders.")
        else:
            self.client.sendServerList(["Builders for %s:" % self.client.world.id] + list(self.client.world.builders))
    
    @info_list
    def commandStatus(self, parts, fromloc, overriderank):
        "/status - Guest\nAliases: mapinfo\nReturns info about the current world"
        self.client.sendServerMessage("%s (%sx%sx%s)" % (self.client.world.id, self.client.world.x, self.client.world.y, self.client.world.z))
        if not self.client.world.owner == "n/a":
            self.client.sendServerMessage("Owner: %s" % (self.client.world.owner))
        self.client.sendNormalMessage(\
            (self.client.world.all_write and "&4Unlocked" or "&2Locked")+" "+\
            (self.client.world.zoned and "&2Zones" or "&4Zones")+" "+\
            (self.client.world.private and "&2Private" or "&4Private")+" "+\
            (self.client.world.physics and "&2Physics" or "&4Physics")+" "+\
            (self.client.world.finite_water and "&4FWater" or "&2FWater")+" "+\
            (self.client.world.admin_blocks and "&2Solids" or "&4Solids")
        )
        if self.client.world.ops:
            self.client.sendServerList(["Ops:"] + list(self.client.world.ops))
        if self.client.world.builders:
            self.client.sendServerList(["Builders:"] + list(self.client.world.builders))
  
    @world_list
    @op_only
    def commandSetspawn(self, parts, fromloc, overriderank):
        "/setspawn - Op\nSets this world's spawn point to the current location."
        x = self.client.x >> 5
        y = self.client.y >> 5
        z = self.client.z >> 5
        h = int(self.client.h*(360/255.0))
        self.client.world.spawn = (x, y, z, h)
        self.client.sendServerMessage("Set spawn point to %s, %s, %s" % (x, y, z))
    
    @info_list
    def commandWhere(self, parts, fromloc, overriderank):
        "/where - Guest\nReturns your current coordinates"
        x = self.client.x >> 5
        y = self.client.y >> 5
        z = self.client.z >> 5
        h = self.client.h
        p = self.client.p
        self.client.sendServerMessage("You are at %s, %s, %s [h%s, p%s]" % (x, y, z, h, p))
