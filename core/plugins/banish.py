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

class BanishPlugin(ProtocolPlugin):
    
    commands = {
        "banish": "commandBanish",
        "worldkick": "commandBanish",
        "worldban": "commandWorldBan",
        "unworldban": "commandUnWorldban",
        "deworldban": "commandUnWorldban",
        "worldbanned": "commandWorldBanned",
    }

    @player_list
    @op_only
    def commandWorldBanned(self, parts, fromloc, overriderank):
        "/worldbanned [page] - Op\nShows who is worldbanned."
        if len(parts)==2:
            try:
                page = int(parts[1])
            except ValueError:
                self.client.sendServerMessage("Page must be a Number.")
                return
        else:
            page = 1
        bannedNames = []
        for element in self.client.world.worldbans.keys():
            bannedNames.append(element)
        if len(bannedNames) > 0:
            bannedNames.sort()
            self.client.sendServerPagedList("WorldBanned:", bannedNames, page)
        else:
            self.client.sendServerList(["WorldBanned: No one."])
    
    @player_list
    @op_only
    @username_command
    def commandBanish(self, user, fromloc, overriderank):
        "/worldkick username - Op\nAliases: banish\nBanishes the user to the default world."
        if user == self.client.world.owner:
            self.client.sendServerMessage("You can't WorldKick the world owner!")
            return
        else:
            if user.world == self.client.world:
                user.sendServerMessage("You were WorldKicked by %s" % self.client.username)
                user.changeToWorld("default")
                self.client.sendServerMessage("User %s was WorldKicked." % user.username)
            else:
                self.client.sendServerMessage("Your user is in another world!")

    @player_list
    @op_only
    @only_username_command
    def commandWorldBan(self, username, fromloc, overriderank):
        "/worldban username - Op\nWorldBan a user from this world."
        if self.client.world.isworldbanned(username):
            self.client.sendServerMessage("%s is already WorldBanned." % username)
            return
        elif self.client.factory.isVisibleStaff(username):
            self.client.sendServerMessage("You can't WorldBan staff!")
            return
        elif self.client.world.isOwner(username):
            self.client.sendServerMessage("You can't WorldBan the world owner!")
            return
        else:
            self.client.world.add_worldban(username)
            if username in self.client.factory.usernames:
                if self.client.factory.usernames[username].world == self.client.world:
                    self.client.factory.usernames[username].changeToWorld("default")
                    self.client.factory.usernames[username].sendServerMessage("You have been WorldBanned by %s" % self.client.username)
            self.client.sendServerMessage("%s has been WorldBanned." % username)

    @player_list
    @op_only
    @only_username_command
    def commandUnWorldban(self, username, fromloc, overriderank):
        "/unworldban username - Op\nAliases: deworldban\nRemoves the WorldBan on the user."
        if not self.client.world.isworldbanned(username):
            self.client.sendServerMessage("%s is not WorldBanned." % username)
        else:
            self.client.world.delete_worldban(username)
            self.client.sendServerMessage("%s was UnWorldBanned." % username)
