# The Nexus software is licensed under the BSD 2-Clause license.
#
# You should have recieved a copy of this license with the software.
# If you did not, you can find one at the following link.
#
# http://opensource.org/licenses/bsd-license.php


from core.plugins import ProtocolPlugin
from core.decorators import *
from core.constants import *
from core.globals import *

class ModsPlugin(ProtocolPlugin):
    
    commands = {
        "staff": "commandStaff",
        "globalbuilders": "commandGlobalBuilders",
        "members": "commandMembers",
        "directors": "commandDirectors",
        "coders": "commandCoders",
        "admins": "commandAdmins",
        "mods": "commandMods",
    }

    @info_list
    def commandStaff(self, parts, fromloc, overriderank):
        "/staff - Guest\nLists all server staff."
        self.client.sendServerMessage("The Server Staff - Owner: "+self.client.factory.owner)
        list = Staff(self)
        for each in list:
            self.client.sendServerList(each)

    @info_list
    def commandGlobalBuilders(self, parts, fromloc, overriderank):
        "/globalbuilders - Guest\nLists all Global Builders."
        if len(self.client.factory.globalbuilders):
            self.client.sendServerList(["Global Builders:"] + list(self.client.factory.globalbuilders))
        else:
            self.client.sendServerList(["Global Builders:"] + list("N/A"))

    @info_list
    def commandMembers(self, parts, fromloc, overriderank):
        "/members - Guest\nLists all Members."
        if len(self.client.factory.members):
            self.client.sendServerList(["Members:"] + list(self.client.factory.members))
        else:
            self.client.sendServerList(["Members:"] + list("N/A"))

    @info_list
    def commandDirectors(self, parts, fromloc, overriderank):
        "/directors - Guest\nLists all Directors."
        if len(self.client.factory.directors):
            self.client.sendServerList(["Directors:"] + list(self.client.factory.directors))
        else:
            self.client.sendServerList(["Directors:"] + list("N/A"))

    @info_list
    def commandCoders(self, parts, fromloc, overriderank):
        "/coders - Guest\nLists all Coders."
        if len(self.client.factory.coders):
            self.client.sendServerList(["Coders:"] + list(self.client.factory.coders))
        else:
            self.client.sendServerList(["Coders:"] + list("N/A"))

    @info_list
    def commandAdmins(self, parts, fromloc, overriderank):
        "/admins - Guest\nLists all Admins."
        if len(self.client.factory.admins):
            self.client.sendServerList(["Admins:"] + list(self.client.factory.admins))
        else:
            self.client.sendServerList(["Admins:"] + list("N/A"))

    @info_list
    def commandMods(self, parts, fromloc, overriderank):
        "/mods - Guest\nLists all Mods."
        if len(self.client.factory.mods):
            self.client.sendServerList(["Mods:"] + list(self.client.factory.mods))
        else:
            self.client.sendServerList(["Mods:"] + list("N/A"))
