#    iCraft is Copyright 2010-2011 both
#
#    The Archives team:
#                   <Adam Guy> adam@adam-guy.com AKA "Adam01"
#                   <Andrew Godwin> andrew@aeracode.org AKA "Aera"
#                   <Dylan Lukes> lukes.dylan@gmail.com AKA "revenant"
#                   <Gareth Coles> colesgareth2@hotmail.com AKA "gdude2002"
#
#    And,
#
#    The iCraft team:
#                   <Andrew Caluzzi> tehcid@gmail.com AKA "tehcid"
#                   <Andrew Dolgov> fox@bah.org.ru AKA "gothfox"
#                   <Andrew Horn> Andrew@GJOCommunity.com AKA "AndrewPH"
#                   <Brad Reardon> brad@bradness.co.cc AKA "PixelEater"
#                   <Clay Sweetser> CDBKJmom@aol.com AKA "Varriount"
#                   <James Kirslis> james@helplarge.com AKA "iKJames"
#                   <Jason Sayre> admin@erronjason.com AKA "erronjason"
#                   <Jonathon Dunford> sk8rjwd@yahoo.com AKA "sk8rjwd"
#                   <Joseph Connor> destroyerx100@gmail.com AKA "destroyerx1"
#                   <Kamyla Silva> supdawgyo@hotmail.com AKA "NotMeh"
#                   <Kristjan Gunnarsson> kristjang@ffsn.is AKA "eugo"
#                   <Nathan Coulombe> NathanCoulombe@hotmail.com AKA "Saanix"
#                   <Nick Tolrud> ntolrud@yahoo.com AKA "ntfwc"
#                   <Noel Benzinger> ronnygmod@gmail.com AKA "Dwarfy"
#                   <Randy Lyne> qcksilverdragon@gmail.com AKA "goober"
#                   <Willem van der Ploeg> willempieeploeg@live.nl AKA "willempiee"
#
#    Disclaimer: Parts of this code may have been contributed by the end-users.
#
#    iCraft is licensed under the Creative Commons
#    Attribution-NonCommercial-ShareAlike 3.0 Unported License. 
#    To view a copy of this license, visit http://creativecommons.org/licenses/by-nc-sa/3.0/
#    Or, send a letter to Creative Commons, 171 2nd Street,
#    Suite 300, San Francisco, California, 94105, USA.

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
