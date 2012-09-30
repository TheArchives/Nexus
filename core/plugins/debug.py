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

import os, shutil, math
from core.plugins import ProtocolPlugin
from core.decorators import *
from core.constants import *
from core.globals import *
from core.world import World

class DebugPlugin(ProtocolPlugin):
    
    commands = {
        "loadedworlds": "commandLoadedWorlds",
        "debugworldsaving": "commandDebugWorldSaving",
        "debugirc": "commandIrc",
        "ircrehash": "commandIrcRehash",
    }

    @coder_only
    def commandLoadedWorlds(self, parts, fromloc, overriderank):
        "/loadedworlds - Coder\nLists all worlds currently loaded."
        self.client.sendServerList(["Loaded Worlds:"] + [id for id, world in self.client.factory.worlds.items()])
        
    @coder_only
    def commandDebugWorldSaving(self, parts, fromloc, overriderank):
        "/debugworldsaving - Coder\nShows data about the given world's saving variables."
        if len(parts) != 2:
            self.client.sendServerMessage("You must enter a world name.")
        else:
            world_id = parts[1].lower()
            if world_id in self.client.factory.worlds:
                world = self.client.factory.worlds[world_id]
                self.client.sendServerMessage("%s world data:" % world_id)
                self.client.sendServerMessage("saving=%s, blockstore.saving=%s" % (world.saving, world.blockstore.saving))
                self.client.sendServerMessage("blockstore.in_queue.qsize()=%s, blockstore.out_queue.qsize()=%s" % (world.blockstore.in_queue.qsize(), world.blockstore.out_queue.qsize()))
            else:
                self.client.sendServerMessage("World '%s' is not loaded." % world_id)
        
    @coder_only
    def commandIrc(self, parts, fromloc, overriderank):
        "/debugirc - Coder\nShows data about the IRC Bot."
        if self.client.factory.irc_relay:
            if self.client.factory.irc_relay.instance:
                self.client.sendServerMessage("IRC Bot running.")
            else:
                self.client.sendServerMessage("No ChatBot running.")
        else:
            self.client.sendServerMessage("No ChatBotFactory running.")
        
    @coder_only
    def commandIrcRehash(self, parts, fromloc, overriderank):
        "/ircrehash - Coder\nAttempts to reload the IRC Bot."
        self.client.sendServerMessage("Attempting to reload the IRC Bot...")
        self.client.factory.reloadIrcBot()
