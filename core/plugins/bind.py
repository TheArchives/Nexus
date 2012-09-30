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

class BindPlugin(ProtocolPlugin):
    
    commands = {
        "bind": "commandBind",
        "b": "commandBind",
        "build": "commandBuild",
        "material": "commandBind",
        "air": "commandAir",
        "stand": "commandAir",
        "place": "commandAir",
    }
    
    hooks = {
        "blockchange": "blockChanged",
        "rankchange": "sendAdminBlockUpdate",
        "canbreakadmin": "canBreakAdminBlocks",
    }
    
    def gotClient(self):
        self.block_overrides = {}
    
    def blockChanged(self, x, y, z, block, selected_block, fromloc):
        "Hook trigger for block changes."
        if block in self.block_overrides:
            return self.block_overrides[block]

    def canBreakAdminBlocks(self):
        "Shortcut for checking permissions."
        if hasattr(self.client, "world"):
            return (not self.client.world.admin_blocks) or self.client.isOpPlus()
        else:
            return False
    
    def sendAdminBlockUpdate(self):
        "Sends a packet that updates the client's admin-building ability"
        self.client.sendPacked(TYPE_INITIAL, 6, "Admincrete Update", "Reloading the server...", self.canBreakAdminBlocks() and 100 or 0)

    @build_list
    def commandBind(self, parts, fromloc, overriderank):
        "/bind blockA blockB - Guest\nAliases: b, material\nBinds blockB to blockA."
        if len(parts) == 1:
            if self.block_overrides:
                temp = tuple(self.block_overrides)
                for each in temp:
                    del self.block_overrides[each]
                self.client.sendServerMessage("All blocks are back to normal.")
                del temp
                return
            self.client.sendServerMessage("Please enter two block types.")
        elif len(parts) == 2:
            try:
                old = ord(self.client.GetBlockValue(parts[1]))
            except:
                return
            if old == None:
                return
            if old in self.block_overrides:
                del self.block_overrides[old]
                self.client.sendServerMessage("%s is back to normal." % parts[1])
            else:
                self.client.sendServerMessage("Please enter two block types.")
        else:
            old = self.client.GetBlockValue(parts[1])
            if old == None:
                return
            old = ord(old)
            new = self.client.GetBlockValue(parts[2])
            if new == None:
                return
            new = ord(new)
            name = parts[2].lower()
            old_name = parts[1].lower()
            self.block_overrides[old] = new
            self.client.sendServerMessage("%s will turn into %s." % (old_name, name))

    @build_list
    def commandAir(self, params, fromloc, overriderank):
        "/air - Guest\nAliases: place, stand\nPuts a block under you for easier building in the air."
        self.client.sendPacked(TYPE_BLOCKSET, self.client.x>>5, (self.client.y>>5)-3, (self.client.z>>5), BLOCK_WHITE)

    @build_list
    def commandBuild(self, parts, fromloc, overrriderank):
        "/build water|watervator|lava|stilllava|grass|doublestep - Guest\nLets you build special blocks."
        if self.client.isOpPlus():
            possibles = {
                "air": (BLOCK_AIR, BLOCK_GLASS, "Glass"),
                "water": (BLOCK_WATER, BLOCK_INDIGO_CLOTH, "Dark Blue cloth"),
                "watervator": (BLOCK_STILL_WATER, BLOCK_BLUE_CLOTH, "Blue cloth"),
                "stillwater": (BLOCK_STILL_WATER, BLOCK_BLUE_CLOTH, "Blue cloth"),
                "lava": (BLOCK_LAVA, BLOCK_ORANGE_CLOTH, "Orange cloth"),
                "stilllava": (BLOCK_STILL_LAVA, BLOCK_RED_CLOTH, "Red cloth"),
                "lavavator": (BLOCK_STILL_LAVA, BLOCK_RED_CLOTH, "Red cloth"),
                "grass": (BLOCK_GRASS, BLOCK_GREEN_CLOTH, "Green cloth"),
                "doublestep": (BLOCK_DOUBLE_STAIR, BLOCK_WOOD, "Wood")
            }
        else:
            possibles = {
                "air": (BLOCK_AIR, BLOCK_GLASS, "Glass"),
                "water": (BLOCK_STILL_WATER, BLOCK_BLUE_CLOTH, "Blue cloth"),
                "watervator": (BLOCK_STILL_WATER, BLOCK_BLUE_CLOTH, "Blue cloth"),
                "stillwater": (BLOCK_STILL_WATER, BLOCK_BLUE_CLOTH, "Blue cloth"),
                "lava": (BLOCK_STILL_LAVA, BLOCK_RED_CLOTH, "Red cloth"),
                "stilllava": (BLOCK_STILL_LAVA, BLOCK_RED_CLOTH, "Red cloth"),
                "lavavator": (BLOCK_STILL_LAVA, BLOCK_RED_CLOTH, "Red cloth"),
                "grass": (BLOCK_GRASS, BLOCK_GREEN_CLOTH, "Green cloth"),
                "doublestep": (BLOCK_DOUBLE_STAIR, BLOCK_WOOD, "Wood")
            }
        if len(parts) == 1:
            self.client.sendServerMessage("Specify a type to toggle.")
        else:
            name = parts[1].lower()
            try:
                new, old, old_name = possibles[name]
            except KeyError:
                self.client.sendServerMessage("'%s' is not a special block type." % name)
            else:
                if old in self.block_overrides:
                    del self.block_overrides[old]
                    self.client.sendServerMessage("%s is back to normal." % old_name)
                else:
                    self.block_overrides[old] = new
                    self.client.sendServerMessage("%s will turn into %s." % (old_name, name))
