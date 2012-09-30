# The Nexus software is licensed under the BSD 2-Clause license.
#
# You should have recieved a copy of this license with the software.
# If you did not, you can find one at the following link.
#
# http://opensource.org/licenses/bsd-license.php


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
