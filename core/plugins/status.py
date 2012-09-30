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
