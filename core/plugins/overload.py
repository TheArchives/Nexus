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

from reqs.twisted.internet import reactor
from core.plugins import ProtocolPlugin
from core.decorators import *
from core.constants import *
from core.world import World

class OverloadPlugin(ProtocolPlugin):
    
    commands = {
        "overload": "commandOverload",
        "sendto": "commandSendTo",
    }
    
    @player_list
    @admin_only
    @username_command
    def commandOverload(self, client, fromloc, overriderank):
        "/overload username - Admin\nSends the users client a massive fake world."
        client.sendOverload()
        self.client.sendServerMessage("Overload sent to %s" % client.username)
        self.client.factory.queue.put((self.client, TASK_SERVERURGENTMESSAGE, "[OVERLOAD] &6%s was overloaded by %s" % (client.username, self.client.username)))

    @player_list
    @mod_only
    def commandSendTo(self, parts, fromloc, overriderank):
        "/send username world - Mod\nSends the users client to another world."
        if len(parts) != 3:
            self.client.sendServerMessage("You must enter username and world.")
        else:
            user = self.client.msgfindUserPartial(parts[1])
            if user is None:
                return
            world_id = parts[2]
            if world_id not in self.client.factory.worlds:
                self.client.sendServerMessage("Attempting to boot '%s'" % world_id)
                try:
                    self.client.factory.loadWorld("worlds/%s" % world_id, world_id)
                except AssertionError:
                    self.client.sendServerMessage("There is no world by that name.")
                    return
            user.changeToWorld(world_id)
            user.sendServerMessage("You were sent to '%s'." % world_id)
            self.client.sendServerMessage("User %s was sent." % user.username)
