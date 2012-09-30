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

class PortalPlugin(ProtocolPlugin):
    
    commands = {
        "p": "commandPortal",
        "tpbox": "commandPortal",
        "phere": "commandPortalhere",
        "pend": "commandPortalend",
        "pshow": "commandShowportals",
        "tpshow": "commandShowportals",
        "pdel": "commandPortaldel",
        "pclear": "commandPortaldel",
        "deltp": "commandPortaldel",
        "pdelend": "commandPortaldelend",
        "puse": "commandUseportals",
    }
    
    hooks = {
        "blockchange": "blockChanged",
        "poschange": "posChanged",
        "newworld": "newWorld",
    }
    
    def gotClient(self):
        self.portal_dest = None
        self.portal_remove = False
        self.portals_on = True
        self.last_block_position = None
    
    def blockChanged(self, x, y, z, block, selected_block, fromloc):
        "Hook trigger for block changes."
        if self.client.world.has_teleport(x, y, z):
            if self.portal_remove:
                self.client.world.delete_teleport(x, y, z)
                self.client.sendServerMessage("You deleted a Portal block.")
            else:
                self.client.sendServerMessage("That is a Portal block, you cannot change it. (/pdel?)")
                return False # False = they weren't allowed to build
        if self.portal_dest:
            self.client.sendServerMessage("You placed a Portal block.")
            self.client.world.add_teleport(x, y, z, self.portal_dest)
    
    def posChanged(self, x, y, z, h, p):
        "Hook trigger for when the user moves"
        rx = x >> 5
        ry = y >> 5
        rz = z >> 5
        try:
            world, tx, ty, tz, th = self.client.world.get_teleport(rx, ry, rz)
        except (KeyError, AssertionError):
            pass
        else:
            # Yes there is! do it.
            if self.portals_on:
                world_id = world
                if world_id not in self.client.factory.worlds:
                    self.client.sendServerMessage("Attempting to boot and join '%s'" % world_id)
                    try:
                        self.client.factory.loadWorld("worlds/%s" % world_id, world_id)
                    except AssertionError:
                        self.client.sendServerMessage("There is no world by that name.")
                        return
                    return
                if (rx, ry, rz) != self.last_block_position:
                    world = self.client.factory.worlds[world_id]
                    if world == self.client.world:
                        self.client.teleportTo(tx, ty, tz, th)
                    elif (self.client.canEnter(world)):
                        self.client.changeToWorld(world.id, position=(tx, ty, tz, th))
                    else:
                        self.client.sendServerMessage(self.client.getReasonCannotEnter(world))
        self.last_block_position = (rx, ry, rz)
    
    def newWorld(self, world):
        "Hook to reset Portal abilities in new worlds if not op."
        if not self.client.isOpPlus():
            self.portal_dest = None
            self.portal_remove = False
            self.portals_on = True
    
    @op_only
    def commandPortal(self, parts, fromloc, overriderank):
        "/p worldname x y z [r] - Op\nAliases: tpbox\nMakes the next block you place a Portal."
        if len(parts) < 5:
            self.client.sendServerMessage("Please enter a worldname and a coord triplet.")
        else:
            try:
                x = int(parts[2])
                y = int(parts[3])
                z = int(parts[4])
            except ValueError:
                self.client.sendServerMessage("All coordinate parameter must be integers.")
            else:
                try:
                    h = int(parts[5])
                except IndexError:
                    h = 0
                except ValueError:
                    self.client.sendServerMessage("r must be an integer.")
                    return
                if not (0 <= h <= 255):
                    self.client.sendServerMessage("r must be between 0 and 255.")
                    return
                self.portal_dest = parts[1], x, y, z, h
                self.client.sendServerMessage("Now you're thinking with Portals. /phere off to stop")
    
    @op_only
    def commandPortalhere(self, parts, fromloc, overriderank):
        "/phere [off] - Op\nEnables Portal creation mode, to here."
        if len(parts) > 1:
            if parts[1].lower() == "off":
                self.portal_dest = None
                self.portal_remove = False
                self.client.sendServerMessage("You are no longer placing Portal blocks.")
            else:
                self.client.sendServerMessage("To turn off portal creation mode specify 'off'.")
        else:
            self.portal_dest = self.client.world.id, self.client.x>>5, self.client.y>>5, self.client.z>>5, self.client.h
            self.client.sendServerMessage("Now you're thinking with Portals. /phere off to stop")
    
    @op_only
    def commandPortalend(self, parts, fromloc, overriderank):
        "/pend - Op\nDisables portal creation mode."
        self.portal_dest = None
        self.portal_remove = False
        self.client.sendServerMessage("You are no longer placing Portal blocks.")
    
    @op_only
    def commandShowportals(self, parts, fromloc, overriderank):
        "/pshow - Op\nAliases: tpshow\nShows all Portal blocks as blue, only to you."
        for offset in self.client.world.teleports.keys():
            x, y, z = self.client.world.get_coords(offset)
            self.client.sendPacked(TYPE_BLOCKSET, x, y, z, BLOCK_BLUE)
        self.client.sendServerMessage("All Portals appearing blue temporarily.")

    @op_only
    def commandPortaldel(self, parts, fromloc, overriderank):
        "/pdel [off|all] - Op\nAliases: deltp, pclear\nEnables Portal deletion mode"
        if len(parts) > 1:
            if parts[1].lower() == "off":
                self.portal_remove = False
                self.client.sendServerMessage("Portal deletion mode ended.")
            elif parts[1].lower() == "all":
                self.client.world.clear_teleports()
                self.client.sendServerMessage("All Portals in this world removed.")
            else:
                self.client.sendServerMessage("You need to specify 'off' or 'all'")
        else:
            self.client.sendServerMessage("You are now able to delete Portals. /pdelend to stop")
            self.portal_remove = True

    @op_only
    def commandPortaldelend(self, parts, fromloc, overriderank):
        "/pdelend - Op\nHere for people that need it, as we're Still Alive."
        self.portal_remove = False
        self.client.sendServerMessage("Portal deletion mode ended.")

    @on_off_command
    def commandUseportals(self, onoff, fromloc, overriderank):
        "/puse on|off - Guest\nAllows you to enable or disable Portal usage."
        if onoff == "on":
            self.portals_on = True
            self.client.sendServerMessage("Portals will now work for you again.")
        else:
            self.portals_on = False
            self.client.sendServerMessage("Portals will no longer work for you.")
