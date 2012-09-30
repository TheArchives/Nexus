# The Nexus software is licensed under the BSD 2-Clause license.
#
# You should have recieved a copy of this license with the software.
# If you did not, you can find one at the following link.
#
# http://opensource.org/licenses/bsd-license.php


import logging
from core.plugins import ProtocolPlugin
from core.decorators import *
from core.constants import *
from core.server import *

class KickBanPlugin(ProtocolPlugin):
    
    commands = {
        "ban": "commandBan",
        "banb": "commandBanBoth",
        "ipban": "commandIpban",
        "ipreason": "commandIpreason",
        "kick": "commandKick",
        "mkick": "commandMassKick",
        "masskick": "commandMassKick",
        "banreason": "commandReason",
        "unban": "commandUnban",
        "unipban": "commandUnipban",
        "banned": "commandBanned",
        "freeze": "commandFreeze",
        "stop": "commandFreeze",
        "unfreeze": "commandUnFreeze",
        "defreeze": "commandUnFreeze",
        "unstop": "commandUnFreeze",
        #"ipshun": "commandIpshun",
        #"unipshun": "commandUnipshun",
        #"ipspec": "commandIpshun",
        #"unipspec": "commandUnipshun",
    }

    @player_list
    @admin_only
    def commandBanned(self, parts, fromloc, overriderank):
        "/banned [page] - Admin\nShows who is Banned."
        if len(parts)==2:
            try:
                page = int(parts[1])
            except ValueError:
                self.client.sendServerMessage("Page must be a Number.")
                return
        else:
            page = 1
        bannedNames = []
        for element in self.client.factory.banned.keys():
            bannedNames.append(element)
        if len(bannedNames) > 0:
            bannedNames.sort()
            self.client.sendServerPagedList("Banned:", bannedNames, page)
        else:
            self.client.sendServerList(["Banned: No one."])

    @player_list
    @mod_only
    @username_command
    def commandKick(self, user, fromloc, overriderank, params=[]):
        "/kick username [reason] - Mod\nKicks the user off the server."
        reason = " ".join(params)
        user.sendErrorAction(ACTION_KICK, self.client, reason)
        self.client.announceGlobal(ACTION_KICK, user.username, reason)
        self.client.sendServerMessage("User %s kicked." % user.username)
        

    @player_list
    @director_only
    def commandMassKick(self, parts, fromloc, overriderank):
        "/mkick - Director\nKicks all users off the server."
        for user in self.client.factory.usernames:
            if user.lower() != self.client.username.lower():
                self.client.factory.usernames[user].sendError("%s kicked everyone!" % self.client.username)
        self.client.factory.queue.put((self.client, TASK_SERVERURGENTMESSAGE, "[MASSKICK] %s kicked everyone." % self.client.username))
    
    @player_list
    @director_only
    @only_username_command
    def commandBanBoth(self, username, fromloc, overriderank, params=[]):
        "/banb username reason - Director\nName and IP ban a user from this server."
        if not params:
            self.client.sendServerMessage("Please give a reason.")
        else:
            if username in self.client.factory.usernames:
                self.commandIpban(["/banb", username] + params, fromloc, overriderank)
            self.commandBan(["/banb", username] + params, fromloc, overriderank)

    @player_list
    @admin_only
    def commandBan(self, parts, fromloc, overriderank):
        "/ban username reason - Admin\nBans the Player from this server."
        username = parts[1].lower()
        if len(parts) <= 1:
            self.client.sendServerMessage("Please specify a reason.")
            return
        if self.client.factory.isBanned(username):
            self.client.sendServerMessage("%s is already banned." % username)
        else:
            reason = " ".join(parts[2:])
            self.client.factory.addBan(username, reason)
            if username in self.client.factory.usernames:
                self.client.factory.usernames[username].sendErrorAction(ACTION_BAN, self.client, reason)
            self.client.announceGlobal(ACTION_BAN, username, reason)
            self.client.sendServerMessage("%s has been banned for %s." % (username, reason))
    
    @director_only
    def commandIpban(self, parts, fromloc, overriderank):
        "/ipban username reason - Director\nBan a user's IP from this server."
        if len(parts) >= 2:
            username = parts[1].lower()
            if username in self.client.factory.usernames:
                ip = self.client.factory.usernames[username].transport.getPeer().host
                if self.client.factory.isIpBanned(ip):
                    self.client.sendServerMessage("%s is already IPBanned." % ip)
                else:
                    reason = " ".join(parts[2:])
                    self.client.factory.addIpBan(ip, reason)
                    self.client.factory.usernames[username].sendErrorAction(ACTION_IPBAN, self.client, reason)
                    self.client.announceGlobal(ACTION_IPBAN, username, reason)
                    self.client.sendServerMessage("%s has been IPBanned." % ip)
            else:
                self.client.sendServerMessage("%s is not online." % username)
        else:
            self.client.sendServerMessage("Please include a user to IPBan.")
    
    @player_list
    @admin_only
    @only_username_command
    def commandUnban(self, username, fromloc, overriderank):
        "/unban username - Admin\nRemoves the Ban on the user."
        if not self.client.factory.isBanned(username):
            self.client.sendServerMessage("%s is not banned." % username)
        else:
            self.client.factory.removeBan(username)
            self.client.announceGlobal(ACTION_UNBAN, username)
            self.client.sendServerMessage("%s has been unbanned." % username)
    
    @player_list
    @director_only
    @only_string_command("IP")
    def commandUnipban(self, ip, fromloc, overriderank):
        "/unipban ip - Director\nRemoves the Ban on the IP."
        if not self.client.factory.isIpBanned(ip):
            self.client.sendServerMessage("%s is not Banned." % ip)
        else:
            self.client.factory.removeIpBan(ip)
            self.client.sendServerMessage("%s UnBanned." % ip)

    @player_list
    @admin_only    
    @only_username_command
    def commandReason(self, username, fromloc, overriderank):
        "/banreason username - Admin\nGives the reason a user was Banned."
        if not self.client.factory.isBanned(username):
            self.client.sendServerMessage("%s is not Banned." % username)
        else:
            self.client.sendServerMessage("Reason: %s" % self.client.factory.banReason(username))
    
    @player_list
    @director_only
    @only_string_command("IP")
    def commandIpreason(self, ip, fromloc, overriderank):
        "/ipreason username - Director\nGives the reason an IP was Banned."
        if not self.client.factory.isIpBanned(ip):
            self.client.sendServerMessage("%s is not Banned." % ip)
        else:
            self.client.sendServerMessage("Reason: %s" % self.client.factory.ipBanReason(ip))

    @player_list
    @mod_only
    def commandUnFreeze(self, parts, fromloc, overriderank):
        "/unfreeze username - Mod\nAliases: defreeze, unstop\nUnfreezes the user, allowing them to move again."
        try:
            username = parts[1]
        except:
            self.client.sendServerMessage("No username given.")
            return
        try:
            user = self.client.factory.usernames[username]
        except:
            self.client.sendServerMessage("User is not online.")
            return
        user.frozen = False
        self.client.sendServerMessage("%s has been unfrozen." % username)
        user.sendNormalMessage("&4You have been unfrozen by %s!" % self.client.username)

    @player_list
    @mod_only
    def commandFreeze(self, parts, fromloc, overriderank):
        "/freeze username - Mod\nAliases: stop\nFreezes the user, preventing them from moving."
        try:
            username = parts[1]
        except:
            self.client.sendServerMessage("No username given.")
            return
        try:
            user = self.client.factory.usernames[username]
        except:
            self.client.sendErrorMessage("User is not online.")
            return
        user.frozen = True
        if self.client.isOnlyHiddenNotVisibleStaff():
            user.sendNormalMessage("&4You have been frozen!")
        else:
            user.sendNormalMessage("&4You have been frozen by %s!" % self.client.username)
        self.client.sendServerMessage("%s has been frozen." % username)

    #@player_list
    #@mod_only
    #@only_username_command
    #def commandIpshun(self, username, fromloc, overriderank):
    #    "/ipspec username - Mod\nAliases: ipshun\nIPSpec a user's IP in this server."
    #    ip = self.client.factory.usernames[username].transport.getPeer().host
    #    if self.client.factory.isIpShunned(ip):
    #        self.client.sendServerMessage("%s is already IPSpecced." % ip)
    #    else:
    #        self.client.factory.addIpShun(ip)
    #        if username in self.client.factory.usernames:
    #            self.client.factory.usernames[username].sendServerMessage("You got IPSpecced!")
    #        self.client.sendServerMessage("%s has been IPSpecced." % ip)
    #        logging.log(logging.INFO,self.client.username + ' IPSpecced ' + username + ip)

    #@player_list
    #@mod_only
    #@only_string_command("IP")
    #def commandUnipshun(self, ip, fromloc, overriderank):
    #    "/unipspec ip - Mod\nAliases: unipshun\nRemoves the IPSpec on the IP."
    #    if not self.client.factory.isIpShunned(ip):
    #        self.client.sendServerMessage("%s is not IPSpecced." % ip)
    #    else:
    #        self.client.factory.removeIpShun(ip)
    #        self.client.sendServerMessage("%s UnIPSpecced." % ip)
    #        logging.log(logging.INFO,self.client.username + ' UnIPSpecced ' + ip)
