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
from reqs.twisted.internet import reactor

class LavaPlugin(ProtocolPlugin):

    hooks = {
        "poschange": "posChanged",
    }

    def gotClient(self):
        self.died = False

    def posChanged(self, x, y, z, h, p):
        "Hook trigger for when the user moves"
        rx = x >> 5
        ry = y >> 5
        rz = z >> 5
        if hasattr(self.client.world.blockstore, "raw_blocks"):
            try: 
                check_offset = self.client.world.blockstore.get_offset(rx, ry, rz)
                try:
                    block = self.client.world.blockstore.raw_blocks[check_offset]
                except (IndexError):
                    return
                check_offset = self.client.world.blockstore.get_offset(rx, ry-1, rz)
                blockbelow = self.client.world.blockstore.raw_blocks[check_offset]
            except (KeyError, AssertionError):
                pass
            else:
                if block == chr(BLOCK_LAVA) or blockbelow == chr(BLOCK_LAVA):
                #or block == chr(BLOCK_STILLLAVA) or blockbelow == chr(BLOCK_STILLLAVA):
                    # Ok, so they touched lava. Warp them to the spawn, timer to stop spam.
                    if self.died is False:
                        self.died = True
                        self.client.teleportTo(self.client.world.spawn[0], self.client.world.spawn[1], self.client.world.spawn[2], self.client.world.spawn[3])
                        self.client.factory.queue.put ((self.client.world,TASK_WORLDMESSAGE, (255, self.client.world, COLOUR_DARKRED+self.client.username+" has died from lava.")))
                        reactor.callLater(1, self.unDie)
                        
    def unDie(self):
        self.died = False
