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

import os
from core.plugins import ProtocolPlugin
from core.decorators import *
from core.constants import *

class CorePlugin(ProtocolPlugin):
    
    commands = {
        "pll": "commandPluginload",
        "plu": "commandPluginunload",
        "plr": "commandPluginreload",
        "pllist": "commandPluginlist",
        "pllistall": "commandPluginlist",
    }
    
    @coder_only
    @only_string_command("plugin name")
    def commandPluginreload(self, plugin_name, fromloc, overriderank):
        try:
            self.client.factory.unloadPlugin(plugin_name)
            self.client.factory.loadPlugin(plugin_name)
        except IOError:
            self.client.sendServerMessage("No such plugin '%s'." % plugin_name)
        else:
            self.client.sendServerMessage("Plugin '%s' reloaded." % plugin_name)
    
    @coder_only
    @only_string_command("plugin name")
    def commandPluginload(self, plugin_name, fromloc, overriderank):
        try:
            self.client.factory.loadPlugin(plugin_name)
        except IOError:
            self.client.sendServerMessage("No such plugin '%s'." % plugin_name)
        else:
            self.client.sendServerMessage("Plugin '%s' loaded." % plugin_name)
    
    @coder_only
    @only_string_command("plugin name")
    def commandPluginunload(self, plugin_name, fromloc, overriderank):
        try:
            self.client.factory.unloadPlugin(plugin_name)
        except IOError:
            self.client.sendServerMessage("No such plugin '%s'." % plugin_name)
        else:
            self.client.sendServerMessage("Plugin '%s' unloaded." % plugin_name)

    @admin_only
    def commandPluginlist(self, parts, fromloc, overriderank):
        "/pllist - Admin\nAliases: pllistall\nShows all plugins."
        pluginlist = os.listdir("core/plugins")
        newpluginlist = []
        for plugin in pluginlist:
            if not plugin.endswith(".pyc"):
                plugin = plugin.replace(".py","")
                newpluginlist.append(plugin)
        self.client.sendServerList(["Plugins:"] + newpluginlist)
