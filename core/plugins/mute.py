# The Nexus software is licensed under the BSD 2-Clause license.
#
# You should have recieved a copy of this license with the software.
# If you did not, you can find one at the following link.
#
# http://opensource.org/licenses/bsd-license.php


from core.plugins import ProtocolPlugin
from core.decorators import *
from core.constants import *

class MutePlugin(ProtocolPlugin):
    
    commands = {
        "mute": "commandMute",
        "unmute": "commandUnmute",
        "muted": "commandMuted",
        "silence": "commandSilence",
        "desilence": "commandDesilence",
        "unsilence": "commandDesilence",
        "silenced": "commandSilenced",
    }
    
    hooks = {
        "recvmessage": "messageReceived",
    }
    
    def gotClient(self):
        self.muted = set()
    
    def messageReceived(self, colour, username, text, action):
        "Stop viewing a message if we've muted them."
        if username.lower() in self.muted:
            return False
    
    @player_list
    @only_username_command
    def commandMute(self, username, fromloc, overriderank):
        "/mute username - Guest\nStops you hearing messages from 'username'."
        self.muted.add(username)
        self.client.sendServerMessage("%s muted." % username)
    
    @player_list
    @only_username_command
    def commandUnmute(self, username, fromloc, overriderank):
        "/unmute username - Guest\nLets you hear messages from this user again"
        if username in self.muted:
            self.muted.remove(username)
            self.client.sendServerMessage("%s unmuted." % username)
        else:
            self.client.sendServerMessage("%s wasn't muted to start with" % username)
    
    @player_list
    def commandMuted(self, username, fromloc, overriderank):
        "/muted - Guest\nLists people you have muted."
        if self.muted:
            self.client.sendServerList(["Muted:"] + list(self.muted))
        else:
            self.client.sendServerMessage("You haven't muted anyone.")
    
    @player_list
    @mod_only
    @only_username_command
    def commandSilence(self, username, fromloc, overriderank):
        "/silence username - Mod\nDisallows the user to talk."
        if self.client.factory.isModPlus(username):
            self.client.sendServerMessage("You cannot silence staff!")
            return
        self.client.factory.silenced.add(username)
        self.client.announceGlobal(ACTION_SILENCE, username)
        self.client.sendServerMessage("%s is now Silenced." % username)

    @player_list
    @mod_only
    @only_username_command
    def commandDesilence(self, username, fromloc, overriderank):
        "/desilence username - Mod\nAliases: unsilence\nAllows the user to talk."
        if self.client.factory.isSilenced(username):
            self.client.factory.silenced.remove(username)
            self.client.announceGlobal(ACTION_UNSILENCE, username)
            self.client.sendServerMessage("%s is no longer Silenced." % username.lower())
        else:
            self.client.sendServerMessage("They aren't silenced.")
    
    @player_list
    @mod_only
    def commandSilenced(self, parts, fromloc, overriderank):
        "/silenced [page] - Mod\nShows who is Silenced."
        if len(parts)==2:
            try:
                page = int(parts[1])
            except ValueError:
                self.client.sendServerMessage("Page must be a Number.")
                return
        else:
            page = 1
        if len(self.client.factory.silenced) > 0:
            silencedNames = list(self.client.factory.silenced)
            silencedNames.sort()
            self.client.sendServerPagedList("Silenced:", silencedNames, page)
        else:
            self.client.sendServerMessage("Silenced: No one.")
