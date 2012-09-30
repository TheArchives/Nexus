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
from ConfigParser import RawConfigParser as ConfigParser
from core.decorators import *

class FetchPlugin(ProtocolPlugin):
    
    commands = {
        "fetch": "commandFetch",
        "bring": "commandFetch",
        "invite": "commandInvite",
        "fp": "commandFetchProtect",
        "fo": "commandFetchOverride",
    }

    hooks = {
        "chatmsg": "message"
    }

    def gotClient(self):
        self.client.var_fetchrequest = False
        self.client.var_fetchdata = ()

    def message(self, message):
        if self.client.var_fetchrequest:
            self.client.var_fetchrequest = False
            if message in ["y", "yes"]:
                sender, world, rx, ry, rz = self.client.var_fetchdata
                if self.client.world == world:
                    self.client.teleportTo(rx, ry, rz)
                else:
                    self.client.changeToWorld(world.id, position=(rx, ry, rz))
                self.client.sendServerMessage("You have accepted the fetch request.")
                sender.sendServerMessage("%s has accepted your fetch request." % self.client.username)
            elif message in ["n", "no"]:
                sender = self.client.var_fetchdata[0]
                self.client.sendServerMessage("You did not accept the fetch request.")
                sender.sendServerMessage("%s did not accept your request." % self.client.username)
            else:
                sender = self.client.var_fetchdata[0]
                self.client.sendServerMessage("You have ignored the fetch request.")
                sender.sendServerMessage("%s has ignored your request." % self.client.username)
                return
            return True
    
    @player_list
    @username_command
    def commandInvite(self, user, fromloc, overriderank):
        "/invite username - Guest\Invites a user to be where you are."
        # Shift the locations right to make them into block coords
        rx = self.client.x >> 5
        ry = self.client.y >> 5
        rz = self.client.z >> 5
        user.var_prefetchdata = (self.client, self.client.world)
        if self.client.world.id == user.world.id:
            user.sendServerMessage("%s would like to fetch you." % self.client.username)
        else:
            user.sendServerMessage("%s would like to fetch you to %s." % (self.client.username, self.client.world.id))
        user.sendServerMessage("Do you wish to accept? [y]es [n]o")
        user.var_fetchrequest = True
        user.var_fetchdata = (self.client, self.client.world, rx, ry, rz)
        self.client.sendServerMessage("The fetch request has been sent.")

    @mod_only
    def commandFetchProtect(self, parts, fromloc, overriderank):
        "/fp on|off - Mod\nToggles Fetch Protection for yourself."
        if len(parts) != 2:
            self.client.sendServerMessage("You must specify either \'on\' or \'off\'.")
        elif parts[1] == "on":
            config = ConfigParser()
            config.read('config/data/fprot.meta')
            config.add_section(self.client.username)
            fp = open('config/data/fprot.meta', "w")
            config.write(fp)
            fp.close()
            self.client.sendServerMessage("Fetch protection is now on.")
        elif parts[1] == "off":
            config = ConfigParser()
            config.read('config/data/fprot.meta')
            config.remove_section(self.client.username)
            fp = open('config/data/fprot.meta', "w")
            config.write(fp)
            fp.close()
            self.client.sendServerMessage("Fetch protection is now off.")
        else:
            self.client.sendServerMessage("You must specify either \'on\' or \'off\'.")

    @player_list
    @admin_only
    @username_command
    def commandFetchOverride(self, user, fromloc, overriderank):
        "/fo username - Mod\nTeleports a user to be where you are"
        # Shift the locations right to make them into block coords
        rx = self.client.x >> 5
        ry = self.client.y >> 5
        rz = self.client.z >> 5
        if user.world == self.client.world:
            user.teleportTo(rx, ry, rz)
        else:
            if self.client.isModPlus():
                user.changeToWorld(self.client.world.id, position=(rx, ry, rz))
            else:
                self.client.sendServerMessage("%s cannot be fetched from '%s'" % (self.client.username, user.world.id))
                return
        user.sendServerMessage("You have been fetched by %s" % self.client.username)
    
    @player_list
    @op_only
    @username_command
    def commandFetch(self, user, fromloc, overriderank):
        "/fetch username - Op\nAliases: bring\nTeleports a user to be where you are"
        # Shift the locations right to make them into block coords
        rx = self.client.x >> 5
        ry = self.client.y >> 5
        rz = self.client.z >> 5
        config = ConfigParser()
        config.read('config/data/fprot.meta')
        if config.has_section(user.username):
            self.client.sendServerMessage("You can't fetch this person; they're Fetch Protected!")
        else:
            if user.world == self.client.world:
                user.teleportTo(rx, ry, rz)
            else:
                if self.client.isModPlus():
                    user.changeToWorld(self.client.world.id, position=(rx, ry, rz))
                else:
                    self.client.sendServerMessage("%s cannot be fetched from '%s'" % (self.client.username, user.world.id))
                    return
            user.sendServerMessage("You have been fetched by %s" % self.client.username)
