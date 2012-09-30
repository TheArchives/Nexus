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
from core.world import World

class ModsPlugin(ProtocolPlugin):
    
    commands = {
        "rank": "commandRank",
        "setrank": "commandRank",
        "derank": "commandDeRank",
        "spec": "commandSpec",
        "unspec": "commandDeSpec",
        "specced": "commandSpecced",
        "writer": "commandOldRanks",
        "builder": "commandOldRanks",
        "globalwriter": "commandOldRanks",
        "globalbuilder": "commandOldRanks",
        "op": "commandOldRanks",
        "mod": "commandOldRanks",
        "admin": "commandOldRanks",
        "coder": "commandOldRanks",
        "director": "commandOldRanks",
        "dewriter": "commandOldDeRanks",
        "debuilder": "commandOldDeRanks",
        "deglobalwriter": "commandOldDeRanks",
        "deglobalbuilder": "commandOldDeRanks",
        "deop": "commandOldDeRanks",
        "demod": "commandOldDeRanks",
        "deadmin": "commandOldDeRanks",
        "decoder": "commandOldDeRanks",
        "dedirector": "commandOldDeRanks",
        "member": "commandOldRanks",
        "demember": "commandOldDeRanks",
    }
        
    @player_list
    @mod_only
    def commandSpecced(self, parts, fromloc, overriderank):
        "/specced [page] - Mod\nShows who is Specced."
        if len(parts)==2:
            try:
                page = int(parts[1])
            except ValueError:
                self.client.sendServerMessage("Page must be a Number.")
                return
        else:
            page = 1
        if len(self.client.factory.spectators) > 0:
            specNames = list(self.client.factory.spectators)
            specNames.sort()
            self.client.sendServerPagedList("Specced:", specNames, page)
        else:
            self.client.sendServerMessage("Specced: No one.")

    @player_list
    @op_only
    def commandRank(self, parts, fromloc, overriderank):
        "/rank rankname username - Op\nAliases: setrank\nMakes username the rank of rankname."
        if len(parts) < 3:
            self.client.sendServerMessage("You must specify a rank and username.")
        else:
            self.client.sendServerMessage(Rank(self, parts, fromloc, overriderank))

    @player_list
    @op_only
    def commandDeRank(self, parts, fromloc, overriderank):
        "/derank rankname username - Op\nMakes username lose the rank of rankname."
        if len(parts) < 3:
            self.client.sendServerMessage("You must specify a rank and username.")
        else:
            self.client.sendServerMessage(DeRank(self, parts, fromloc, overriderank))

    @player_list
    @op_only
    def commandOldRanks(self, parts, fromloc, overriderank):
        "/rankname username [world] - Op\nAliases: member, (global)writer, (global)builder, op, mod, admin, director\nThis is here for Myne users."
        if len(parts) < 2:
            self.client.sendServerMessage("You must specify a rank and username.")
        else:
            if parts[0] == "/writer":
                parts[0] = "/builder"
            elif parts[0] == "/globalwriter":
                parts[0] = "/globalbuilder"
            parts = ["/rank", parts[0][1:]] + parts[1:]
            self.client.sendServerMessage(Rank(self, parts, fromloc, overriderank))

    @player_list
    @op_only
    def commandOldDeRanks(self, parts, fromloc, overriderank):
        "/derankname username [world] - Op\nAliases: de(global)member, de(global)writer, debuilder, deop, demod, deadmin, dedirector\nThis is here for Myne users."
        if len(parts) < 2:
            self.client.sendServerMessage("You must specify a rank and username.")
        else:
            if parts[0] == "/dewriter":
                parts[0] = "/debuilder"
            elif parts[0] == "/deglobalwriter":
                parts[0] = "/deglobalbuilder"
            parts = ["/derank", parts[0][3:]] + parts[1:]
            self.client.sendServerMessage(DeRank(self, parts, fromloc, overriderank))

    @player_list
    @mod_only
    @only_username_command
    def commandSpec(self, username, fromloc, overriderank):
        "/spec username - Mod\nMakes the user as a spec."
        self.client.sendServerMessage(Spec(self, username, fromloc, overriderank))
     
    @player_list
    @mod_only
    @only_username_command
    def commandDeSpec(self, username, fromloc, overriderank):
        "/unspec username - Mod\nRemoves the user as a spec."
        try:
            self.client.factory.spectators.remove(username)
        except:
            self.client.sendServerMessage("%s was never a spec." % username)
        self.client.sendServerMessage("%s is no longer a spec." % username)
        if username in self.client.factory.usernames:
            self.client.factory.usernames[username].sendSpectatorUpdate()
