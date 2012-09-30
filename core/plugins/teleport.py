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
