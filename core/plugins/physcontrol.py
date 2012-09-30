# The Nexus software is licensed under the BSD 2-Clause license.
#
# You should have recieved a copy of this license with the software.
# If you did not, you can find one at the following link.
#
# http://opensource.org/licenses/bsd-license.php


from core.plugins import ProtocolPlugin
from core.decorators import *
from core.constants import *

class PhysicsControlPlugin(ProtocolPlugin):
    
    commands = {
        "physics": "commandPhysics",
        "physflush": "commandPhysflush",
        "unflood": "commandUnflood",
        "deflood": "commandUnflood",
        "fwater": "commandFwater",
    }
    
    @world_list
    @op_only
    def commandUnflood(self, parts, fromloc, overriderank):
        "/unflood worldname - Op\nAliases: deflood\nSlowly removes all water and lava from the world."
        self.client.world.start_unflooding()
        self.client.sendWorldMessage("Unflooding has been initiated.")
    
    @world_list
    @admin_only
    @on_off_command
    def commandPhysics(self, onoff, fromloc, overriderank):
        "/physics on|off - Admin\nEnables or disables physics in this world."
        if onoff == "on":
            if self.client.world.physics:
                self.client.sendWorldMessage("Physics is already on here.")
            else:
                if self.client.factory.numberWithPhysics() >= self.client.factory.physics_limit:
                    self.client.sendWorldMessage("There are already %s worlds with physics on (the max)." % self.client.factory.physics_limit)
                else:
                    self.client.world.physics = True
                    self.client.sendWorldMessage("This world now has physics enabled.")
        else:
            if not self.client.world.physics:
                self.client.sendWorldMessage("Physics is already off here.")
            else:
                self.client.world.physics = False
                self.client.sendWorldMessage("This world now has physics disabled.")
    
    @world_list
    @op_only
    @on_off_command
    def commandFwater(self, onoff, fromloc, overriderank):
        "/fwater on|off - Op\nEnables or disables finite water in this world."
        if onoff == "on":
            self.client.world.finite_water = True
            self.client.sendWorldMessage("This world now has finite water enabled.")
        else:
            self.client.world.finite_water = False
            self.client.sendWorldMessage("This world now has finite water disabled.")

    @world_list
    @admin_only
    def commandPhysflush(self, parts, fromloc, overriderank):
        "/physflush - Admin\nTells the physics engine to rescan the world."
        if self.client.world.physics:
            if self.client.factory.numberWithPhysics() >= self.client.factory.physics_limit:
                self.client.sendWorldMessage("There are already %s worlds with physics on (the max)." % self.client.factory.physics_limit)
            else:
                self.client.world.physics = False
                self.client.world.physics = True
                self.client.sendWorldMessage("This world now has a physics flush running.")
        else:
            self.client.sendServerMessage("This world does not have physics on.")
