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

import cPickle
from core.plugins import ProtocolPlugin
from core.decorators import *

class TitlePlugin(ProtocolPlugin):
    
    commands = {
        "tag":     "commandSetTag",
        "settag":     "commandSetTag",
    }
    
    # System methods, not for commands
    def loadRank(self):
        file = open('config/data/tags.dat', 'r')
        rank_dic = cPickle.load(file)
        file.close()
        return rank_dic
    
    def dumpRank(self, bank_dic):
        file = open('config/data/tags.dat', 'w')
        cPickle.dump(bank_dic, file)
        file.close()
    
    @player_list
    @director_only
    def commandSetTag(self, parts, fromloc, overriderank):
        "/tag [tag] username - Director\nAliases: settag\nGives or removes a tag to username."
        if len(parts)>2:
            rank = self.loadRank()
            user = parts[1].lower()
            rank[user] = (" ".join(parts[2:]))
            self.dumpRank(rank)
            if len(" ".join(parts[2:]))<8:
                self.client.sendServerMessage("Added the tag of: "+(" ".join(parts[2:])))
            else:
                self.client.sendServerMessage("Added the tag of: "+(" ".join(parts[2:])))
        elif len(parts)==2:
            rank = self.loadRank()
            user = parts[1].lower()
            if user not in rank:
                self.client.sendServerMessage("Syntax: /tag tag username")
                return False
            else:
                rank.pop(user)
                self.dumpRank(rank)
                self.client.sendServerMessage("Removed the tag.")
