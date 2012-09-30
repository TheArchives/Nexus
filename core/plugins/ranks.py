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
from core.globals import *
from core.world import World

class ModsPlugin(ProtocolPlugin):
    
    commands = {
        "rank": "commandRank",
        "setrank": "commandRank",
        "derank": "commandDeRank",
        "spec": "commandSpec",
        "unspec": "commandDeSpec",
        "specced": "commandSpecced",
        "writer": "commandOldRanks",
        "builder": "commandOldRanks",
        "globalwriter": "commandOldRanks",
        "globalbuilder": "commandOldRanks",
        "op": "commandOldRanks",
        "mod": "commandOldRanks",
        "admin": "commandOldRanks",
        "coder": "commandOldRanks",
        "director": "commandOldRanks",
        "dewriter": "commandOldDeRanks",
        "debuilder": "commandOldDeRanks",
        "deglobalwriter": "commandOldDeRanks",
        "deglobalbuilder": "commandOldDeRanks",
        "deop": "commandOldDeRanks",
        "demod": "commandOldDeRanks",
        "deadmin": "commandOldDeRanks",
        "decoder": "commandOldDeRanks",
        "dedirector": "commandOldDeRanks",
        "member": "commandOldRanks",
        "demember": "commandOldDeRanks",
    }
        
    @player_list
    @mod_only
    def commandSpecced(self, parts, fromloc, overriderank):
        "/specced [page] - Mod\nShows who is Specced."
        if len(parts)==2:
            try:
                page = int(parts[1])
            except ValueError:
                self.client.sendServerMessage("Page must be a Number.")
                return
        else:
            page = 1
        if len(self.client.factory.spectators) > 0:
            specNames = list(self.client.factory.spectators)
            specNames.sort()
            self.client.sendServerPagedList("Specced:", specNames, page)
        else:
            self.client.sendServerMessage("Specced: No one.")

    @player_list
    @op_only
    def commandRank(self, parts, fromloc, overriderank):
        "/rank rankname username - Op\nAliases: setrank\nMakes username the rank of rankname."
        if len(parts) < 3:
            self.client.sendServerMessage("You must specify a rank and username.")
        else:
            self.client.sendServerMessage(Rank(self, parts, fromloc, overriderank))

    @player_list
    @op_only
    def commandDeRank(self, parts, fromloc, overriderank):
        "/derank rankname username - Op\nMakes username lose the rank of rankname."
        if len(parts) < 3:
            self.client.sendServerMessage("You must specify a rank and username.")
        else:
            self.client.sendServerMessage(DeRank(self, parts, fromloc, overriderank))

    @player_list
    @op_only
    def commandOldRanks(self, parts, fromloc, overriderank):
        "/rankname username [world] - Op\nAliases: member, (global)writer, (global)builder, op, mod, admin, director\nThis is here for Myne users."
        if len(parts) < 2:
            self.client.sendServerMessage("You must specify a rank and username.")
        else:
            if parts[0] == "/writer":
                parts[0] = "/builder"
            elif parts[0] == "/globalwriter":
                parts[0] = "/globalbuilder"
            parts = ["/rank", parts[0][1:]] + parts[1:]
            self.client.sendServerMessage(Rank(self, parts, fromloc, overriderank))

    @player_list
    @op_only
    def commandOldDeRanks(self, parts, fromloc, overriderank):
        "/derankname username [world] - Op\nAliases: de(global)member, de(global)writer, debuilder, deop, demod, deadmin, dedirector\nThis is here for Myne users."
        if len(parts) < 2:
            self.client.sendServerMessage("You must specify a rank and username.")
        else:
            if parts[0] == "/dewriter":
                parts[0] = "/debuilder"
            elif parts[0] == "/deglobalwriter":
                parts[0] = "/deglobalbuilder"
            parts = ["/derank", parts[0][3:]] + parts[1:]
            self.client.sendServerMessage(DeRank(self, parts, fromloc, overriderank))

    @player_list
    @mod_only
    @only_username_command
    def commandSpec(self, username, fromloc, overriderank):
        "/spec username - Mod\nMakes the user as a spec."
        self.client.sendServerMessage(Spec(self, username, fromloc, overriderank))
     
    @player_list
    @mod_only
    @only_username_command
    def commandDeSpec(self, username, fromloc, overriderank):
        "/unspec username - Mod\nRemoves the user as a spec."
        try:
            self.client.factory.spectators.remove(username)
        except:
            self.client.sendServerMessage("%s was never a spec." % username)
        self.client.sendServerMessage("%s is no longer a spec." % username)
        if username in self.client.factory.usernames:
            self.client.factory.usernames[username].sendSpectatorUpdate()
