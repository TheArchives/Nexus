# The Nexus software is licensed under the BSD 2-Clause license.
#
# You should have recieved a copy of this license with the software.
# If you did not, you can find one at the following link.
#
# http://opensource.org/licenses/bsd-license.php


from core.plugins import ProtocolPlugin
from core.decorators import *

class BanishPlugin(ProtocolPlugin):
    
    commands = {
        "banish": "commandBanish",
        "worldkick": "commandBanish",
        "worldban": "commandWorldBan",
        "unworldban": "commandUnWorldban",
        "deworldban": "commandUnWorldban",
        "worldbanned": "commandWorldBanned",
    }

    @player_list
    @op_only
    def commandWorldBanned(self, parts, fromloc, overriderank):
        "/worldbanned [page] - Op\nShows who is worldbanned."
        if len(parts)==2:
            try:
                page = int(parts[1])
            except ValueError:
                self.client.sendServerMessage("Page must be a Number.")
                return
        else:
            page = 1
        bannedNames = []
        for element in self.client.world.worldbans.keys():
            bannedNames.append(element)
        if len(bannedNames) > 0:
            bannedNames.sort()
            self.client.sendServerPagedList("WorldBanned:", bannedNames, page)
        else:
            self.client.sendServerList(["WorldBanned: No one."])
    
    @player_list
    @op_only
    @username_command
    def commandBanish(self, user, fromloc, overriderank):
        "/worldkick username - Op\nAliases: banish\nBanishes the user to the default world."
        if user == self.client.world.owner:
            self.client.sendServerMessage("You can't WorldKick the world owner!")
            return
        else:
            if user.world == self.client.world:
                user.sendServerMessage("You were WorldKicked by %s" % self.client.username)
                user.changeToWorld("default")
                self.client.sendServerMessage("User %s was WorldKicked." % user.username)
            else:
                self.client.sendServerMessage("Your user is in another world!")

    @player_list
    @op_only
    @only_username_command
    def commandWorldBan(self, username, fromloc, overriderank):
        "/worldban username - Op\nWorldBan a user from this world."
        if self.client.world.isworldbanned(username):
            self.client.sendServerMessage("%s is already WorldBanned." % username)
            return
        elif self.client.factory.isVisibleStaff(username):
            self.client.sendServerMessage("You can't WorldBan staff!")
            return
        elif self.client.world.isOwner(username):
            self.client.sendServerMessage("You can't WorldBan the world owner!")
            return
        else:
            self.client.world.add_worldban(username)
            if username in self.client.factory.usernames:
                if self.client.factory.usernames[username].world == self.client.world:
                    self.client.factory.usernames[username].changeToWorld("default")
                    self.client.factory.usernames[username].sendServerMessage("You have been WorldBanned by %s" % self.client.username)
            self.client.sendServerMessage("%s has been WorldBanned." % username)

    @player_list
    @op_only
    @only_username_command
    def commandUnWorldban(self, username, fromloc, overriderank):
        "/unworldban username - Op\nAliases: deworldban\nRemoves the WorldBan on the user."
        if not self.client.world.isworldbanned(username):
            self.client.sendServerMessage("%s is not WorldBanned." % username)
        else:
            self.client.world.delete_worldban(username)
            self.client.sendServerMessage("%s was UnWorldBanned." % username)
