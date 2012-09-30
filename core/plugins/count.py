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
from core.timer import ResettableTimer

class CountPlugin(ProtocolPlugin):
    
    commands = {
        "count": "commandCount",
        "countdown": "commandCount",
    }

    def gotClient(self):
        self.num = int(0)

    @op_only
    def commandCount(self, parts, fromloc, overriderank):
        "/count [number] - Op\nAliases: countdown\nCounts down from 3 or from number given (up to 15)"
        if self.num != 0:
            self.client.sendServerMessage("You can only have one count at a time!")
            return
        if len(parts) > 1:
            try:
                self.num = int(parts[1])
            except ValueError:
                self.client.sendServerMessage("Number must be an integer!")
                return
        else:
            self.num = 3
        if self.num > 15:
            self.client.sendServerMessage("You can't count from higher than 15!")
            self.num = 0
            return
        counttimer = ResettableTimer(self.num, 1, self.sendgo, self.sendcount)
        self.client.sendPlainWorldMessage("&7COUNTDOWN: &c%s" %self.num)
        counttimer.start()

    def sendgo(self):
        self.client.sendPlainWorldMessage("&7GET SET: &aGO!")
        self.num = 0

    def sendcount(self, count):
        if int(self.num)-int(count) == 1:
            self.client.sendPlainWorldMessage("&7GET READY: &e1")
        elif not int(self.num)-int(count) == 0:
            self.client.sendPlainWorldMessage("&7COUNTDOWN: &c%s" %(int(self.num)-int(count)))
