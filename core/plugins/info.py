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

class InfoPlugin(ProtocolPlugin):
    BlockList = []
    while len(BlockList) != 50:
        BlockList.append('')
    BlockList[0]="air"
    BlockList[1]="rock"
    BlockList[2]="grass"
    BlockList[3]="dirt"
    BlockList[4]="stone"
    BlockList[5]="wood"
    BlockList[6]="plant"
    BlockList[7]="adminblock"
    BlockList[8]="water"
    BlockList[9]="still_water"
    BlockList[10]="lava"
    BlockList[11]="still_lava"
    BlockList[12]="sand"
    BlockList[13]="gravel"
    BlockList[14]="goldore"
    BlockList[15]="ironore"
    BlockList[16]="coal"
    BlockList[17]="log"
    BlockList[18]="leaves"
    BlockList[19]="sponge"
    BlockList[20]="glass"
    BlockList[21]="red"
    BlockList[22]="orange"
    BlockList[23]="yellow"
    BlockList[24]="lime"
    BlockList[25]="green"
    BlockList[26]="turquoise"
    BlockList[27]="cyan"
    BlockList[28]="blue"
    BlockList[29]="indigo"
    BlockList[30]="violet"
    BlockList[31]="purple"
    BlockList[32]="magenta"
    BlockList[33]="pink"
    BlockList[34]="black"
    BlockList[35]="grey"
    BlockList[36]="white"
    BlockList[37]="yellow_flower"
    BlockList[38]="red_flower"
    BlockList[39]="brown_mushroom"
    BlockList[40]="red_mushroom"
    BlockList[41]="gold"
    BlockList[42]="iron"
    BlockList[43]="step"
    BlockList[44]="doublestep"
    BlockList[45]="brick"
    BlockList[46]="tnt"
    BlockList[47]="bookcase"
    BlockList[48]="moss"
    BlockList[49]="obsidian"

    hooks = {
        "preblockchange": "blockChanged",
    }

    commands = {
        "binfo": "commandInfo",
        "bget": "commandInfo",
        "rget": "commandInfo",
        "pget": "commandInfo",
    }
    
    def gotClient(self):
        self.binfo = False
    
    def blockChanged(self, x, y, z, block, selected_block, fromloc):
        if self.binfo == 1:
            check_offset = self.client.world.blockstore.get_offset(x, y, z)
            block2 = ord(self.client.world.blockstore.raw_blocks[check_offset])
            if block2 == 0:
                self.client.sendServerMessage("Block Info: %s (%s)" % (self.BlockList[block], block))
                self.client.sendServerMessage("x: %s y: %s z: %s" % (x, y, z))
                return block2
            else:
                self.client.sendServerMessage("Block Info: %s (%s)" % (self.BlockList[block2], block2))
                self.client.sendServerMessage("x: %s y: %s z: %s" % (x, y, z))
                return block2
            
    @build_list
    def commandInfo(self, parts, fromloc, overriderank):
        "/binfo [blockname/on/off] - Guest\nStarts getting information on blocks. Toggle."
        if len(parts) != 2:
            self.client.sendServerMessage("Please enter a block to get the ID of or specify on/off.")
        elif parts[1] != "on" and parts[1] != "off":
            try:
                block = globals()['BLOCK_%s' % parts[1].upper()]
            except KeyError:
                self.client.sendServerMessage("'%s' is not a valid block name." % parts[1])
                return
            self.client.sendServerMessage("%s is BlockID %s" % (parts[1],block))
        elif parts[1] == "on":
            self.binfo = True
            self.client.sendServerMessage("You are now getting info about blocks.")
        elif parts[1] == "off":
            self.binfo = False
            self.client.sendServerMessage("You are no longer getting info about blocks.")