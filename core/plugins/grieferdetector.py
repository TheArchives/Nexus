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

import logging, datetime
from core.plugins import ProtocolPlugin
from core.decorators import *
from core.constants import *
from reqs.twisted.internet import reactor

class GreiferDetectorPlugin(ProtocolPlugin):

    hooks = {
        "blockchange": "blockChanged",
        "newworld": "newWorld",
    }
    
    def gotClient(self):
        self.var_blockchcount = 0
        self.in_publicworld = False
    
    def blockChanged(self, x, y, z, block, selected_block, fromloc):
        "Hook trigger for block changes."
        world = self.client.world
        if block is BLOCK_AIR and self.in_publicworld:
            if ord(world.blockstore.raw_blocks[world.blockstore.get_offset(x, y, z)]) != 3:
                worldname = world.id
                username = self.client.username
                def griefcheck():
                    if self.var_blockchcount >= self.client.factory.grief_blocks:
                        self.client.factory.queue.put((self.client, TASK_STAFFMESSAGE, ("#%s%s: %s%s" % (COLOUR_DARKGREEN, 'Console ALERT', COLOUR_DARKRED, "Possible grief behavior was detected;", False))))
                        self.client.factory.queue.put((self.client, TASK_STAFFMESSAGE, ("#%s%s: %s%s" % (COLOUR_DARKGREEN, 'Console ALERT', COLOUR_DARKRED, "World: "+worldname+" | User: "+username, False))))
                        self.client.logger.warning("%s was detected as a possible griefer in world %s." % (username, worldname))
                        self.client.adlog.write(datetime.datetime.utcnow().strftime("%Y/%m/%d %H:%M:%S")+" | #Console ALERT: Possible grief behavior was detected; World: "+worldname+" | User: "+username+"\n")
                        self.client.adlog.flush()
                    self.var_blockchcount = 0
                if self.var_blockchcount == 0:
                    reactor.callLater(self.client.factory.grief_time, griefcheck)
                self.var_blockchcount += 1
                
    def newWorld(self, world):
        "Hook to reset portal abilities in new worlds if not op."
        if world.id.find('public') == -1:
            self.in_publicworld = False
            self.var_blockchcount = 0
        else:
            self.in_publicworld = True
