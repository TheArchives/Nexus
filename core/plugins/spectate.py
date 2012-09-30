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

class SpectatePlugin(ProtocolPlugin):
    
    commands = {
        "spectate": "commandSpectate",
        "follow": "commandSpectate",
        "watch": "commandSpectate",
        "possess": "commandPossess",
    }
    
    hooks = {
        "poschange": "posChanged",
    }
    
    def gotClient(self):
        self.flying = False
        self.last_flying_block = None
    
    def posChanged(self, x, y, z, h, p):
        "Hook trigger for when the user moves"

        spectators = set()

        for uid in self.client.factory.clients:
            user = self.client.factory.clients[uid]

            try:
                if user.spectating == self.client.id:
                    if user.x != x or user.y != y or user.z != z:
                        user.teleportTo(x >> 5, y >> 5, z >> 5, h, p)
            except AttributeError:
                pass
            try:
               if self.client.possessing == user.id:
                    if user.x != x or user.y != y or user.z != z:
                        user.teleportTo(x >> 5, y >> 5, z >> 5, h, p)
            except AttributeError:
                pass
   
    @player_list
    @op_only
    @username_command
    def commandSpectate(self, user, fromloc, overriderank):
        "/spectate username - Guest\nAliases: follow, watch\nFollows specified user around"

        nospec_check = True

        try:
            self.client.spectating
        except AttributeError:
            nospec_check = False

        if not nospec_check or self.client.spectating != user.id:
            self.client.sendServerMessage("You are now spectating %s" % user.username)
            self.client.spectating = user.id
        else:
            self.client.sendServerMessage("You are no longer spectating %s" % user.username)
            self.client.spectating = False

    @player_list
    @director_only
    @username_command
    def commandPossess(self, user, fromloc, overriderank):
        "/possess username - Admin\nControls the specified user"

        nopossess_check = True

        try:
            self.client.possessing
        except AttributeError:
            nopossess_check = False

        if not nopossess_check or self.client.possessing != user.id:
            self.client.sendServerMessage("You are now possessing %s." % user.username)
            self.client.possessing = user.id
        else:
            self.client.sendServerMessage("You are no longer possessing %s." % user.username)
            self.client.possessing = False

