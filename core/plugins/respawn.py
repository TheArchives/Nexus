# The Nexus software is licensed under the BSD 2-Clause license.
#
# You should have recieved a copy of this license with the software.
# If you did not, you can find one at the following link.
#
# http://opensource.org/licenses/bsd-license.php


from core.plugins import ProtocolPlugin
from core.decorators import *
from core.constants import *

class FetchPlugin(ProtocolPlugin):
    
    commands = {
        "respawn": "commandRespawn",
    }
    
    @player_list
    @mod_only
    @only_username_command
    def commandRespawn(self, username, fromloc, rankoverride):
           "/respawn username - Mod\nRespawns the user."
           if username in self.client.factory.usernames:
               self.client.factory.usernames[username].respawn()
           else:
                self.client.sendServerMessage("%s is not on the server." % username)
                return
           self.client.factory.usernames[username].sendServerMessage("You have been respawned by %s." % self.client.username)
           self.client.sendServerMessage("%s respawned." % username)
