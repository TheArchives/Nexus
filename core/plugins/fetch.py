# The Nexus software is licensed under the BSD 2-Clause license.
#
# You should have recieved a copy of this license with the software.
# If you did not, you can find one at the following link.
#
# http://opensource.org/licenses/bsd-license.php


from core.plugins import ProtocolPlugin
from ConfigParser import RawConfigParser as ConfigParser
from core.decorators import *

class FetchPlugin(ProtocolPlugin):
    
    commands = {
        "fetch": "commandFetch",
        "bring": "commandFetch",
        "invite": "commandInvite",
        "fp": "commandFetchProtect",
        "fo": "commandFetchOverride",
    }

    hooks = {
        "chatmsg": "message"
    }

    def gotClient(self):
        self.client.var_fetchrequest = False
        self.client.var_fetchdata = ()

    def message(self, message):
        if self.client.var_fetchrequest:
            self.client.var_fetchrequest = False
            if message in ["y", "yes"]:
                sender, world, rx, ry, rz = self.client.var_fetchdata
                if self.client.world == world:
                    self.client.teleportTo(rx, ry, rz)
                else:
                    self.client.changeToWorld(world.id, position=(rx, ry, rz))
                self.client.sendServerMessage("You have accepted the fetch request.")
                sender.sendServerMessage("%s has accepted your fetch request." % self.client.username)
            elif message in ["n", "no"]:
                sender = self.client.var_fetchdata[0]
                self.client.sendServerMessage("You did not accept the fetch request.")
                sender.sendServerMessage("%s did not accept your request." % self.client.username)
            else:
                sender = self.client.var_fetchdata[0]
                self.client.sendServerMessage("You have ignored the fetch request.")
                sender.sendServerMessage("%s has ignored your request." % self.client.username)
                return
            return True
    
    @player_list
    @username_command
    def commandInvite(self, user, fromloc, overriderank):
        "/invite username - Guest\Invites a user to be where you are."
        # Shift the locations right to make them into block coords
        rx = self.client.x >> 5
        ry = self.client.y >> 5
        rz = self.client.z >> 5
        user.var_prefetchdata = (self.client, self.client.world)
        if self.client.world.id == user.world.id:
            user.sendServerMessage("%s would like to fetch you." % self.client.username)
        else:
            user.sendServerMessage("%s would like to fetch you to %s." % (self.client.username, self.client.world.id))
        user.sendServerMessage("Do you wish to accept? [y]es [n]o")
        user.var_fetchrequest = True
        user.var_fetchdata = (self.client, self.client.world, rx, ry, rz)
        self.client.sendServerMessage("The fetch request has been sent.")

    @mod_only
    def commandFetchProtect(self, parts, fromloc, overriderank):
        "/fp on|off - Mod\nToggles Fetch Protection for yourself."
        if len(parts) != 2:
            self.client.sendServerMessage("You must specify either \'on\' or \'off\'.")
        elif parts[1] == "on":
            config = ConfigParser()
            config.read('config/data/fprot.meta')
            config.add_section(self.client.username)
            fp = open('config/data/fprot.meta', "w")
            config.write(fp)
            fp.close()
            self.client.sendServerMessage("Fetch protection is now on.")
        elif parts[1] == "off":
            config = ConfigParser()
            config.read('config/data/fprot.meta')
            config.remove_section(self.client.username)
            fp = open('config/data/fprot.meta', "w")
            config.write(fp)
            fp.close()
            self.client.sendServerMessage("Fetch protection is now off.")
        else:
            self.client.sendServerMessage("You must specify either \'on\' or \'off\'.")

    @player_list
    @admin_only
    @username_command
    def commandFetchOverride(self, user, fromloc, overriderank):
        "/fo username - Mod\nTeleports a user to be where you are"
        # Shift the locations right to make them into block coords
        rx = self.client.x >> 5
        ry = self.client.y >> 5
        rz = self.client.z >> 5
        if user.world == self.client.world:
            user.teleportTo(rx, ry, rz)
        else:
            if self.client.isModPlus():
                user.changeToWorld(self.client.world.id, position=(rx, ry, rz))
            else:
                self.client.sendServerMessage("%s cannot be fetched from '%s'" % (self.client.username, user.world.id))
                return
        user.sendServerMessage("You have been fetched by %s" % self.client.username)
    
    @player_list
    @op_only
    @username_command
    def commandFetch(self, user, fromloc, overriderank):
        "/fetch username - Op\nAliases: bring\nTeleports a user to be where you are"
        # Shift the locations right to make them into block coords
        rx = self.client.x >> 5
        ry = self.client.y >> 5
        rz = self.client.z >> 5
        config = ConfigParser()
        config.read('config/data/fprot.meta')
        if config.has_section(user.username):
            self.client.sendServerMessage("You can't fetch this person; they're Fetch Protected!")
        else:
            if user.world == self.client.world:
                user.teleportTo(rx, ry, rz)
            else:
                if self.client.isModPlus():
                    user.changeToWorld(self.client.world.id, position=(rx, ry, rz))
                else:
                    self.client.sendServerMessage("%s cannot be fetched from '%s'" % (self.client.username, user.world.id))
                    return
            user.sendServerMessage("You have been fetched by %s" % self.client.username)
