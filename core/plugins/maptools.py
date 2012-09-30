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

class PrivatePlugin(ProtocolPlugin):
    
    commands = {
        "private": "commandPrivate",
        "lock": "commandLock",
        #"ponly": "commandPOnly"
    }
    
    @world_list
    @op_only
    @on_off_command
    def commandPrivate(self, onoff, fromloc, overriderank):
        "/private on|off - Op\nEnables or disables the private status for this world."
        if onoff == "on":
            self.client.world.private = True
            self.client.sendWorldMessage("This world is now private.")
            self.client.sendServerMessage("%s is now private." % self.client.world.id)
        else:
            self.client.world.private = False
            self.client.sendWorldMessage("This world is now public.")
            self.client.sendServerMessage("%s is now public." % self.client.world.id)

    @world_list
    @op_only
    @on_off_command
    def commandLock(self, onoff, fromloc, overriderank):
        "/lock on|off - Op\nEnables or disables the world lock."
        if onoff == "on":
            self.client.world.all_write = False
            self.client.sendWorldMessage("This world is now locked.")
            self.client.sendServerMessage("Locked %s" % self.client.world.id)
        else:
            self.client.world.all_write = True
            self.client.sendWorldMessage("This world is now unlocked.")
            self.client.sendServerMessage("Unlocked %s" % self.client.world.id)

    #@op_only
    #@on_off_command
    #def commandPOnly(self, onoff, fromloc, rankoverride):
        #"/ponly on/off - Makes the world only accessable by portals."
        #if onoff == "on":
            #self.client.world.portal_only = True
            #self.client.sendWorldMessage("This world is now portal only.")
            #self.client.sendServerMessage("%s is now only accessable through portals." % self.client.world.id)
        #else:
            #self.client.world.portal_only = False
            #elf.client.sendWorldMessage("This world is now accesable through commands.")
            #self.client.sendServerMessage("%s is now accessable through commands." % self.client.world.id)
