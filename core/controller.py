# The Nexus software is licensed under the BSD 2-Clause license.
#
# You should have recieved a copy of this license with the software.
# If you did not, you can find one at the following link.
#
# http://opensource.org/licenses/bsd-license.php


import logging, traceback, os
import json as simplejson
from reqs.twisted.protocols.basic import LineReceiver
from reqs.twisted.internet.protocol import Factory

class ControllerProtocol(LineReceiver):
    """
    Protocol for dealing with controller requests.
    """
    def connectionMade(self):
        self.logger = logging.getLogger("Controller")
        peer = self.transport.getPeer()
        self.logger.debug("Control connection made from %s:%s" % (peer.host, peer.port))
        self.factory, self.controller_factory = self.factory.main_factory, self.factory

    def connectionLost(self, reason):
        peer = self.transport.getPeer()
        self.logger.debug("Control connection lost from %s:%s" % (peer.host, peer.port))

    def sendJson(self, data):
        self.sendLine(simplejson.dumps(data))

    def lineReceived(self, line):
        data = simplejson.loads(line)
        peer = self.transport.getPeer()
        if data['password'] != self.factory.controller_password:
            self.sendJson({"error": "invalid password"})
            self.logger.info("Control: Invalid password %s (%s:%s)" % (data, peer.host, peer.port))
        else:
            command = data['command'].lower()
            try:
                func = getattr(self, "command%s" % command.title())
            except AttributeError:
                self.sendJson({"error": "unknown command %s" % command})
            else:
                self.logger.debug("Control: %s %s (%s:%s)" % (command.upper(), data, peer.host, peer.port))
                try:
                    func(data)
                except Exception, e:
                    self.sendJson({"error": "%s" % e})
                    traceback.print_exc()

    def commandName(self, data):
        self.sendJson({"name": self.factory.server_name})

    def commandMOTD(self, data):
        self.sendJson({"motd": self.factory.server_message})

    def commandGreeting(self, data):
        self.sendJson({"greeting": self.factory.initial_greeting})

    def commandPublic(self, data):
        self.sendJson({"public": self.factory.public})

    def commandLimit(self, data):
        self.sendJson({"limit": self.factory.max_clients})

    def commandDuplicates(self, data):
        self.sendJson({"duplicates": self.factory.duplicate_logins})

    def commandPhLimits(self, data):
        self.sendJson({"phlimits": self.factory.physics_limit})

    def commandAwayTime(self, data):
        self.sendJson({"awaytime": self.factory.away_time})

    def commandDefault(self, data):
        self.sendJson({"default": self.factory.default_name})

    def commandDeBackup(self, data):
        self.sendJson({"debackup": self.factory.default_backup})

    def commandASD(self, data):
        self.sendJson({"asd": self.factory.asd_delay})

    def commandGChat(self, data):
        self.sendJson({"gchat": self.factory.gchat})

    def commandBUFreq(self, data):
        if self.factory.backup_auto:
            self.sendJson({"bufreq": self.factory.backup_freq})
        else:
            self.sendJson({"bufreq": "N/A"})

    def commandBUMax(self, data):
        if self.factory.backup_auto:
            self.sendJson({"bumax": self.factory.backup_max})
        else:
            self.sendJson({"bumax": "N/A"})

    def commandCurrency(self, data):
        self.sendJson({"currency": self.factory.currency})

    def commandBDLimit(self, data):
        self.sendJson({"bdlimit": self.factory.build_director})

    def commandBALimit(self, data):
        self.sendJson({"balimit": self.factory.build_admin})

    def commandBMLimit(self, data):
        self.sendJson({"bmlimit": self.factory.build_mod})

    def commandBOPLimit(self, data):
        self.sendJson({"boplimit": self.factory.build_op})

    def commandBOLimit(self, data):
        self.sendJson({"bolimit": self.factory.build_other})

    def commandIRCServer(self, data):
        if self.factory.use_irc:
            if self.factory.irc_config.get("irc", "server") == "bots.esper.net":
                self.sendJson({"ircserver": "irc.esper.net"})
            else:
                self.sendJson({"ircserver": self.factory.irc_config.get("irc", "server")})
        else:
            self.sendJson({"ircserver": "N/A"})

    def commandIRCChannel(self, data):
        if self.factory.use_irc:
            self.sendJson({"ircchannel": self.factory.irc_channel})
            self.sendJson({"staffchatchannel": self.factory.staffchat_channel})
        else:
            self.sendJson({"ircchannel": "N/A"})
            self.sendJson({"staffchatchannel": "N/A"})

    def commandUsers(self, data):
        self.sendJson({"users": [client.username for client in self.factory.clients.values() if client.username]})

    def commandOwner(self, data):
        self.sendJson({"owner": self.factory.owner})

    def commandHidden(self, data):
        self.sendJson({"hidden": list(self.factory.hidden)})

    def commandDirectors(self, data):
        self.sendJson({"directors": list(self.factory.directors)})

    def commandCoders(self, data):
        self.sendJson({"admins": list(self.factory.coders)})

    def commandAdmins(self, data):
        self.sendJson({"admins": list(self.factory.admins)})

    def commandMods(self, data):
        self.sendJson({"mods": list(self.factory.mods)})

    def commandGlobalBuilders(self, data):
        self.sendJson({"globalbuilders": list(self.factory.globalbuilders)})

    def commandMembers(self, data):
        self.sendJson({"members": list(self.factory.members)})

    def commandSpecs(self, data):
        self.sendJson({"specs": list(self.factory.spectators)})

    def commandWorlds(self, data):
        self.sendJson({"worlds": list(self.factory.worlds.keys())})

    def commandUserworlds(self, data):
        self.sendJson({"worlds": [
            (world.id, [client.username for client in world.clients if client.username], {
                "id": world.id,
                "ops": list(world.ops),
                "builders": list(world.builders),
                "private": world.private,
                "archive": world.is_archive,
                "locked": not world.all_write,
                "physics": world.physics,
                "zones": world.zoned,
                "colors": world.highlight_ops,
                "fwater": world.finite_water,
                "solids": world.admin_blocks,
                "x": world.x,
                "y": world.y,
                "z": world.z,
                "owner": world.owner,
            })
            for world in self.factory.worlds.values()
        ]})

    def commandWorldinfo(self, data):
        world = self.factory.worlds[data['world_id']]
        self.sendJson({
            "id": world.id,
            "ops": list(world.ops),
            "builders": list(world.builders),
            "private": world.private,
            "archive": world.is_archive,
            "locked": not world.all_write,
            "physics": world.physics,
            "zones": world.zoned,
            "colors": world.highlight_ops,
            "fwater": world.finite_water,
            "solids": world.admin_blocks,
            "x": world.x,
            "y": world.y,
            "z": world.z,
            "owner": world.owner,
        })

class ControllerFactory(Factory):
    protocol = ControllerProtocol

    def __init__(self, main_factory):
        self.main_factory = main_factory
