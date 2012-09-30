# The Nexus software is licensed under the BSD 2-Clause license.
#
# You should have recieved a copy of this license with the software.
# If you did not, you can find one at the following link.
#
# http://opensource.org/licenses/bsd-license.php


from reqs.twisted.internet import reactor
from core.plugins import ProtocolPlugin
from core.decorators import *
from core.constants import *
from core.world import World

class OverloadPlugin(ProtocolPlugin):
    
    commands = {
        "overload": "commandOverload",
        "sendto": "commandSendTo",
    }
    
    @player_list
    @admin_only
    @username_command
    def commandOverload(self, client, fromloc, overriderank):
        "/overload username - Admin\nSends the users client a massive fake world."
        client.sendOverload()
        self.client.sendServerMessage("Overload sent to %s" % client.username)
        self.client.factory.queue.put((self.client, TASK_SERVERURGENTMESSAGE, "[OVERLOAD] &6%s was overloaded by %s" % (client.username, self.client.username)))

    @player_list
    @mod_only
    def commandSendTo(self, parts, fromloc, overriderank):
        "/send username world - Mod\nSends the users client to another world."
        if len(parts) != 3:
            self.client.sendServerMessage("You must enter username and world.")
        else:
            user = self.client.msgfindUserPartial(parts[1])
            if user is None:
                return
            world_id = parts[2]
            if world_id not in self.client.factory.worlds:
                self.client.sendServerMessage("Attempting to boot '%s'" % world_id)
                try:
                    self.client.factory.loadWorld("worlds/%s" % world_id, world_id)
                except AssertionError:
                    self.client.sendServerMessage("There is no world by that name.")
                    return
            user.changeToWorld(world_id)
            user.sendServerMessage("You were sent to '%s'." % world_id)
            self.client.sendServerMessage("User %s was sent." % user.username)
