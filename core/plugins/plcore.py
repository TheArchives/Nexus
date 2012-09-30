# The Nexus software is licensed under the BSD 2-Clause license.
#
# You should have recieved a copy of this license with the software.
# If you did not, you can find one at the following link.
#
# http://opensource.org/licenses/bsd-license.php


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
