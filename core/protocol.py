# The Nexus software is licensed under the BSD 2-Clause license.
#
# You should have recieved a copy of this license with the software.
# If you did not, you can find one at the following link.
#
# http://opensource.org/licenses/bsd-license.php

import os, logging, hashlib, traceback, datetime, cPickle, math
from reqs.twisted.internet.protocol import Protocol
from reqs.twisted.internet import reactor
from core.constants import *
from core.plugins import protocol_plugins
from core.decorators import *
from core.irc_client import ChatBotFactory

class CoreServerProtocol(Protocol):
    """
    Main protocol class for communicating with clients.
    Commands are mainly provided by plugins (protocol plugins).
    """

    def connectionMade(self):
        "We've got a TCP connection, let's set ourselves up."
        self.logger = logging.getLogger("Client")
        # We use the buffer because TCP is a stream protocol :)
        self.buffer = ""
        self.loading_world = False
        # Load plugins for ourselves
        self.identified = False
        self.commands = {}
        self.hooks = {}
        self.plugins = [plugin(self) for plugin in protocol_plugins]
        self.ClientVars = dict()
        # Set identification variable to false
        self.identified = False
        # Get an ID for ourselves
        try:
            self.id = self.factory.claimId(self)
        except ServerFull:
            self.sendError("This server is full from all of the users.")
            return
        # Open the Whisper Log, Adminchat log and WorldChat Log
        self.whisperlog = open("logs/whisper.log", "a")
        self.wclog = open("logs/world.log", "a")
        # Check for IP bans
        ip = self.transport.getPeer().host
        if self.factory.isIpBanned(ip):
            self.sendError("You are Banned for: %s" % self.factory.ipBanReason(ip))
            return
        self.logger.debug("Assigned ID %i" % self.id)
        self.factory.joinWorld(self.factory.default_name, self)
        self.sent_first_welcome = False
        self.read_only = False
        self.username = None
        self.old_username = None
        self.selected_archive_name = None
        self.initial_position = None
        self.last_block_changes = []
        self.last_block_position = (-1, -1, -1)
        self.gone = 0
        self.frozen = False
        self.resetIdleTimer()
        # initialize these immediately, just in case someone tries to read them before the user first loads a level
        self.x = 0
        self.y = 0
        self.z = 0
        self.h = 0
        self.p = 0

    def registerCommand(self, command, func):
        "Registers func as the handler for the command named 'command'."
        # Make sure case doesn't matter
        command = command.lower()
        # Warn if already registered
#        if command in self.commands:
#            self.logger.warn("Command '%s' is already registered. Overriding." % command)
        # Register
        self.commands[command] = func

    def unregisterCommand(self, command, func):
        "Unregisters func as command's handler, if it is currently the handler."
        # Make sure case doesn't matter
        command = command.lower()
        try:
            if self.commands[command] == func:
                del self.commands[command]
        except KeyError:
            self.logger.warn("Command '%s' is not registered to %s." % (command, func))

    def registerHook(self, hook, func):
        "Registers func as something to be run for hook 'hook'."
        if hook not in self.hooks:
            self.hooks[hook] = []
        self.hooks[hook].append(func)

    def unregisterHook(self, hook, func):
        "Unregisters func from hook 'hook'."
        try:
            self.hooks[hook].remove(func)
        except (KeyError, ValueError):
            self.logger.warn("Hook '%s' is not registered to %s." % (command, func))

    def unloadPlugin(self, plugin_class):
        "Unloads the given plugin class."
        for plugin in self.plugins:
            if isinstance(plugin, plugin_class):
                self.plugins.remove(plugin)
                plugin.unregister()

    def loadPlugin(self, plugin_class):
        self.plugins.append(plugin_class(self))

    def runHook(self, hook, *args, **kwds):
        "Runs the hook 'hook'."
        for func in self.hooks.get(hook, []):
            result = func(*args, **kwds)
            # If they return False, we can skip over and return
            if result is not None:
                return result
        return None

    def queueTask(self, task, data=[], world=None):
        "Adds the given task to the factory's queue."
        # If they've overridden the world, use that as the client.
        if world:
            self.factory.queue.put((
                world,
                task,
                data,
            ))
        else:
            self.factory.queue.put((
                self,
                task,
                data,
            ))

    def stopIdleTimer(self):
        if hasattr(self, "idleCB"):
            if self.idleCB.active():
                self.idleCB.cancel()

    def resetIdleTimer(self):
        self.stopIdleTimer()
        if self.gone or not self.factory.away_kick:
            return
        if self.username:
            if not self.isModPlus():
                self.idleCB = reactor.callLater(60*self.factory.away_time, self.onIdleKick)

    def onIdleKick(self):
        self.sendError("You were away too long.")
        #self.factory.queue.put((self, TASK_SERVERURGENTMESSAGE, "[IDLE] &e%s was away too long." % self.username))
        return

    def sendWorldMessage(self, message):
        "Sends a message to everyone in the current world."
        self.queueTask(TASK_WORLDMESSAGE, (255, self.world, COLOUR_YELLOW+message))

    def sendPlainWorldMessage(self, message):
        "Sends a message to everyone in the current world, without any added color."
        self.queueTask(TASK_WORLDMESSAGE, (255, self.world, message))

    def connectionLost(self, reason):
        # Leave the world
        try:
            self.factory.leaveWorld(self.world, self)
        except (KeyError, AttributeError):
            pass
        # Remove ourselves from the username list
        if self.username:
            self.factory.recordPresence(self.username)
            try:
                if self.factory.usernames[self.username.lower()] is self:
                    del self.factory.usernames[self.username.lower()]
            except KeyError:
                pass
        # Remove from ID list, send removed msgs
        self.factory.releaseId(self.id)
        self.factory.queue.put((self, TASK_PLAYERLEAVE, (self.id,)))
        if self.username:
            self.logger.info("Disconnected '%s'" % (self.username))
            self.runHook("playerquit", self.username)
            self.logger.debug("(reason: %s)" % (reason))
        # Kill all plugins
        self.stopIdleTimer()
        del self.plugins
        del self.commands
        del self.hooks
        self.connected = 0

    def send(self, data):
        self.transport.write(data)

    def sendPacked(self, mtype, *args):
        fmt = TYPE_FORMATS[mtype]
        self.transport.write(chr(mtype) + fmt.encode(*args))

    def sendError(self, error):
        self.logger.info("Sending error: %s" % error)
        self.sendPacked(TYPE_ERROR, error)
        reactor.callLater(0.2, self.transport.loseConnection)

    def duplicateKick(self):
        "Called when someone else logs in with our username"
        self.sendError("You logged in on another computer.")

    def packString(self, string, length=64, packWith=" "):
        return string + (packWith*(length-len(string)))

        
    # These are convenience pass-throughs for rank checking the user. These just be direct calls with no special handling.
    # If you need to understand the details or think you need to add special handling, look at the functions in the factory object (server.py)
        
    def isServerOwner(self):
        return self.factory.isServerOwner(self.username)

    def isHidden(self):
        return self.factory.isHidden(self.username)

    def isDirector(self):
        return self.factory.isDirector(self.username)

    def isCoder(self):
        return self.factory.isCoder(self.username)

    def isAdmin(self):
        return self.factory.isAdmin(self.username)
        
    def isMod(self):
        return self.factory.isMod(self.username)

    def isHiddenPlus(self):
        return self.factory.isHiddenPlus(self.username)

    def isDirectorPlus(self):
        return self.factory.isDirectorPlus(self.username)

    def isCoderPlus(self):
        return self.factory.isCoderPlus(self.username)

    def isAdminPlus(self):
        return self.factory.isAdminPlus(self.username)
        
    def isModPlus(self):
        return self.factory.isModPlus(self.username)
        
    def isStaff(self):
        return self.factory.isStaff(self.username)
        
    def isVisibleStaff(self):
        return self.factory.isVisibleStaff(self.username)
        
    def isOnlyHiddenNotVisibleStaff(self):
        return self.factory.isOnlyHiddenNotVisibleStaff(self.username)

        
    def isWorldOwner(self):
        return self.world.isOwner(self.username)

    def isOp(self):
        return self.world.isOp(self.username)

    def isBuilder(self):
        return self.world.isBuilder(self.username)
        
    def isWorldOwnerPlus(self):
        return self.isWorldOwner() or self.isModPlus()

    def isOpPlus(self):
        return self.isOp() or self.isWorldOwnerPlus()

    def isBuilderPlus(self):
        return self.isBuilder() or self.isOpPlus()
        
        
    def isMember(self):
        return self.factory.isMember(self.username)
        
    def isMemberPlus(self):
        return self.isMember or self.isBuilderPlus()
        
    def isSpectator(self):
        return self.factory.isSpectator(self.username)

    def isSilenced(self):
        return self.factory.isSilenced(self.username)

        
    # Returns a list of all users currently online that contain the given name string.
    def matchPartialUsername(self, name):
        matches = []
        nameLower = name.lower()
        for username in self.factory.usernames:
            if nameLower in username:
                matches.append(username)
        return matches
        
    # Attempts to find the given username in the list of those currently online. Either returns the corresponding user object or None.
    def findUserExact(self, name):
        nameLower = name.lower()
        if nameLower in self.factory.usernames:
            return self.factory.usernames[nameLower]
        else:
            return None
        
    # Searches all online usernames for those containing the given text. If only a single user matches, then this returns that corresponding user object. Otherwise, None.
    def findUserPartial(self, name):
        users = self.matchPartialUsername(name)
        if len(users)==1:
            return user[0]
        else:
            return None
            
    # Attempts to find the given username in the list of those currently online. Either returns the corresponding user object or None.
    # If no user count be found, this prints a message to the user explaining why.
    def msgfindUserExact(self, name):
        if len(name) == 0:
            self.sendServerMessage("Please specify a username.")
            return None
        else:
            nameLower = name.lower()
            if nameLower in self.factory.usernames:
                return self.factory.usernames[nameLower]
            else:
                self.sendServerMessage("No such user '%s'" % name)
                return None
            
    # Searches all online usernames for those containing the given text. If only a single user matches, then this returns that corresponding user object. Otherwise, None.
    # If either no user count be match or there were multiple matches, this prints a message to the user explaining the problem.
    def msgfindUserPartial(self, name):
        if len(name) == 0:
            self.sendServerMessage("Please specify a username.")
            return None
        else:
            nameLower = name.lower()
            # Try to match as a full name first.
            if nameLower in self.factory.usernames:
                return self.factory.usernames[nameLower]
            # Build a list of any partial matches.
            matches = []
            for username in self.factory.usernames:
                if nameLower in username:
                    matches.append(username)
            if len(matches)==0:
                self.sendServerMessage("No such user '%s' (3+ chars?)" % name)
                return None
            elif len(matches) > 1:
                self.sendServerMessage("'%s' matches multiple users. Be more specific." % name)
                return None
            else:
                return self.factory.usernames[matches[0]]

    # Evaluates if the user and enter the given world. All code should use this, so that we have consistency.
    def canEnter(self, world):
        # world-owners and staff are always allowed
        # worldbans exclude anyone else (including builder and op)
        # builder and op are allowed into private worlds
        # otherwise the world cannot be private
        if (world.isOwner(self.username) or self.isVisibleStaff()):
            return True
        elif (world.isWorldbanned(self.username)):
            return False
        elif (world.isOp(self.username) or world.isBuilder(self.username)):
            return True
        elif (world.private):
            return False
        else:
            return True
            
    # If canEnter has returned False, then this will give the reason string which can be output to the user.
    def getReasonCannotEnter(self, world):
        if (world.isWorldbanned(self.username)):
            return "You are WorldBanned from '%s'; so you're not allowed in." % world.id
        elif (world.private):
            return "'%s' is private; you're not allowed in." % world.id
        else:
            # This shouldn't happen.
            return "Unknown reason."

    def dataReceived(self, data):
        # First, add the data we got onto our internal buffer
        self.buffer += data
        # While there's still data there...
        while self.buffer:
            # Examine the first byte, to see what the command is
            type = ord(self.buffer[0])
            try:
                format = TYPE_FORMATS[type]
            except KeyError:
                # it's a weird data packet, probably a ping.
                reactor.callLater(0.2, self.transport.loseConnection)
                return
            # See if we have all its data
            if len(self.buffer) - 1 < len(format):
                # Nope, wait a bit
                break
            # OK, decode the data
            parts = list(format.decode(self.buffer[1:]))
            self.buffer = self.buffer[len(format)+1:]
            if type == TYPE_INITIAL:
                # Get the client's details
                protocol, self.username, mppass, utype = parts
                self.old_username = self.username
                if self.identified == True:
                    self.logger.info("Kicked '%s'; already logged in to server" % (self.username))
                    self.sendError("You already logged in! Foolish bot owners.")
                # Check their password
                correct_pass = hashlib.md5(self.factory.salt + self.username).hexdigest()[-32:].strip("0")
                mppass = mppass.strip("0")
                if not self.transport.getHost().host.split(".")[0:2] == self.transport.getPeer().host.split(".")[0:2]:
                    if mppass != correct_pass:
                        self.logger.info("Kicked '%s'; invalid password (%s, %s)" % (self.username, mppass, correct_pass))
                        self.sendError("Incorrect authentication. Connect normally instead of Resume.")
                        return
                if "@" in self.username:
                    self.username = "~" + self.username.split("@")[0]
                    self.logger = logging.getLogger(self.username)
                    self.logger.info("Connected, as '%s' (%s)" % (self.username, self.old_username))
                else:
                    self.logger = logging.getLogger(self.username)
                    self.logger.info("Connected, as '%s'" % self.username)
                self.identified = True
                # Are they banned?
                if (self.factory.isBanned(self.username) or self.factory.isBanned(self.old_username)):
                    self.sendError("You are Banned for: %s" % self.factory.banReason(self.username))
                    return
                # OK, see if there's anyone else with that username
                if not self.factory.duplicate_logins and self.username.lower() in self.factory.usernames:
                    self.factory.usernames[self.username.lower()].duplicateKick()
                self.factory.usernames[self.username.lower()] = self
                # Right protocol?
                if protocol != 7:
                    self.sendError("Wrong protocol.")
                    break
                # Send them back our info.
                breakable_admins = self.runHook("canbreakadmin")
                self.sendPacked(
                    TYPE_INITIAL,
                    7, # Protocol version
                    self.packString(self.factory.server_name),
                    self.packString(self.factory.server_message),
                    100 if breakable_admins else 0,
                )
                # Then... this other stuff
                for client in self.factory.usernames.values():
                    if self.username.lower() in INFO_VIPLIST and not self.isModPlus():
                        client.sendNormalMessage(COLOUR_DARKRED+"iCraft Developer spotted;")
                    if client.isVisibleStaff():
                        client.sendNormalMessage("%s[+] %s%s &ehas come online." % (COLOUR_DARKGREEN, self.userColour(), self.username))
                    else:
                        client.sendServerMessage("%s[+] %s has come online." % (COLOUR_DARKGREEN, self.username))
                    if self.username.lower() in self.factory.lastseen:
                        client.sendNormalMessage(COLOUR_PURPLE+"Welcome back, %s." % self.username)
                    else:
                        client.sendNormalMessage(COLOUR_PURPLE+"Welcome to the server, %s!" % self.username)
                if self.factory.irc_relay:
                    self.factory.irc_relay.sendServerMessage("3[+] %s%s 07has come online." % (self.userColour(), self.username))
                    if self.username.lower() not in self.factory.lastseen:
                        # Duplicate welcome messages to IRC, so that staff there can have a clue when someone is entirely new.
                        self.factory.irc_relay.sendServerMessage("%sWelcome to the server, %s!" % (COLOUR_PURPLE, self.username))
                reactor.callLater(0.1, self.sendLevel)
                reactor.callLater(1, self.sendKeepAlive)
                self.resetIdleTimer()
            elif type == TYPE_BLOCKCHANGE:
                x, y, z, created, block = parts
                if block == 255:
                    block = 0
                if block > 49:
                    self.logger.info("Kicked '%s'; Tried to place an invalid block.; Block: '%s'" % (self.transport.getPeer().host, block))
                    self.sendError("Invalid blocks are not allowed!")
                    return
                if 6 < block < 12:
                    if not block == 9 and not block == 11:
                        self.logger.info("Kicked '%s'; Tried to place an invalid block.; Block: '%s'" % (self.transport.getPeer().host, block))
                        self.sendError("Invalid blocks are not allowed!")
                        return
                if self.identified == False:
                    self.logger.info("Kicked '%s'; did not send a login before building" % (self.transport.getPeer().host))
                    self.sendError("Provide an authentication before building.")
                    return
                try:
                # If we're read-only, reverse the change
                    if self.isSpectator():
                        self.sendBlock(x, y, z)
                        self.sendServerMessage("Specs cannot edit worlds.")
                        return
                    allowbuild = self.runHook("blockclick", x, y, z, block, "user")
                    if allowbuild is False:
                        self.sendBlock(x, y, z)
                        return
                    elif not self.AllowedToBuild(x, y, z):
                        self.sendBlock(x, y, z)
                        return
                    # This try prevents out-of-range errors on the world storage
                    # Track if we need to send back the block change
                    overridden = False
                    selected_block = block
                    # If we're deleting, block is actually air
                    # (note the selected block is still stored as selected_block)
                    if not created:
                        block = 0
                    # Pre-hook, for stuff like /paint
                    new_block = self.runHook("preblockchange", x, y, z, block, selected_block, "user")
                    if new_block is not None:
                        block = new_block
                        overridden = True
                    # Call hooks
                    new_block = self.runHook("blockchange", x, y, z, block, selected_block, "user")
                    if new_block is False:
                        # They weren't allowed to build here!
                        self.sendBlock(x, y, z)
                        continue
                    elif new_block is True:
                        # Someone else handled building, just continue
                        continue
                    elif new_block is not None:
                        block = new_block
                        overridden = True
                    # OK, save the block
                    self.world[x, y, z] = chr(block)
                    # Now, send the custom block back if we need to
                    if overridden:
                        self.sendBlock(x, y, z, block)
                # Out of bounds!
                except (KeyError, AssertionError):
                    self.sendPacked(TYPE_BLOCKSET, x, y, z, "\0")
                # OK, replay changes to others
                else:
                    self.factory.queue.put((self, TASK_BLOCKSET, (x, y, z, block)))
                    if len(self.last_block_changes) >= 2:
                        self.last_block_changes = [(x, y, z)] + self.last_block_changes[:1]+self.last_block_changes[1:2]
                    else:
                        self.last_block_changes = [(x, y, z)] + self.last_block_changes[:1]
                self.resetIdleTimer()
            elif type == TYPE_PLAYERPOS:
                # If we're loading a world, ignore these.
                if self.loading_world:
                    continue
                naff, x, y, z, h, p = parts
                pos_change = not (x == self.x and y == self.y and z == self.z)
                dir_change = not (h == self.h and p == self.p)
                if dir_change:
                    self.resetIdleTimer()
                if self.frozen:
                    newx = self.x >> 5
                    newy = self.y >> 5
                    newz = self.z >> 5
                    self.teleportTo(newx, newy, newz, h, p)
                    return
                override = self.runHook("poschange", x, y, z, h, p)
                # Only send changes if the hook didn't say no
                if override is not False:
                    if pos_change:
                        # Send everything to the other clients
                        self.factory.queue.put((self, TASK_PLAYERPOS, (self.id, self.x, self.y, self.z, self.h, self.p)))
                    elif dir_change:
                        self.factory.queue.put((self, TASK_PLAYERDIR, (self.id, self.h, self.p)))
                self.x, self.y, self.z, self.h, self.p = x, y, z, h, p
            elif type == TYPE_MESSAGE:
                # We got a message.
                byte, message = parts
                override = self.runHook("chatmsg", message)
                goodchars = ["a", "b", "c", "d", "e", "f", "g", "h", "i", "j", "k", "l", "m", "n", "o", "p", "q", "r", "s", "t", "u", "v", "w", "x", "y", "z", "0", "1", "2", "3", "4", "5", "6", "7", "8", "9", " ", "!", "@", "#", "$", "%", "*", "(", ")", "-", "_", "+", "=", "{", "[", "}", "]", ":", ";", "\"", "\'", "<", ",", ">", ".", "?", "/", "\\", "|", "^", "`", "~"]
                for c in message.lower():
                    if not c in goodchars:
                        self.client.sendErrorMessage("Invalid characters are not allowed!")
                        return
                message = message.replace("%0", "&0")
                message = message.replace("%1", "&1")
                message = message.replace("%2", "&2")
                message = message.replace("%3", "&3")
                message = message.replace("%4", "&4")
                message = message.replace("%5", "&5")
                message = message.replace("%6", "&6")
                message = message.replace("%7", "&7")
                message = message.replace("%8", "&8")
                message = message.replace("%9", "&9")
                message = message.replace("%a", "&a")
                message = message.replace("%b", "&b")
                message = message.replace("%c", "&c")
                message = message.replace("%d", "&d")
                message = message.replace("%e", "&e")
                message = message.replace("%f", "&f")
                message = message.replace("0", "&f")       #TODO Fish - Aren't these color codes already taken care of by the irc bot's code?
                message = message.replace("00", "&f")
                message = message.replace("1", "&0")
                message = message.replace("01", "&0")
                message = message.replace("2", "&1")
                message = message.replace("02", "&1")
                message = message.replace("3", "&2")
                message = message.replace("03", "&2")
                message = message.replace("4", "&c")
                message = message.replace("04", "&c")
                message = message.replace("5", "&4")
                message = message.replace("05", "&4")
                message = message.replace("6", "&5")
                message = message.replace("06", "&5")
                message = message.replace("7", "&6")
                message = message.replace("07", "&6")
                message = message.replace("8", "&e")
                message = message.replace("08", "&e")
                message = message.replace("9", "&a")
                message = message.replace("09", "&a")
                message = message.replace("10", "&3")
                message = message.replace("11", "&b")
                message = message.replace("12", "&9")
                message = message.replace("13", "&d")
                message = message.replace("14", "&8")
                message = message.replace("15", "&7")
                message = message.replace("./", " /")
                message = message.replace(".!", " !")
                message = message.replace(".@", " @")
                message = message.replace(".#", " #")
                message = message.replace(".$", " $")
                message = message.replace(".+", " +")
                message = message.replace(".=", " =")
                message = message.replace("%*", "^")
                message = message.replace("%$rnd", "&$rnd")
                if message[len(message)-2] == "&":
                    self.sendServerMessage("You cannot use a color at the end of a message")
                    return
                if len(message) > 51:
                    moddedmsg = message[:51].replace(" ", "")
                    if moddedmsg[len(moddedmsg)-2] == "&":
                        message = message.replace("&", "*")
                if self.identified == False:
                    self.logger.info("Kicked '%s'; did not send a login before chatting; Message: '%s'" % (self.transport.getPeer().host, message))
                    self.sendError("Provide an authentication before chatting.")
                    return
                if message.startswith("/"):
                    # It's a command
                    parts = [x.strip() for x in message.split() if x.strip()]
                    command = parts[0].strip("/")
                    self.logger.info("%s just used: %s" % (self.username," ".join(parts)))
                    # for command logging to IRC
                    if self.factory.irc_relay:
                        if self.factory.irc_cmdlogs:
                            self.factory.irc_relay.sendServerMessage("07%s just used: %s" % (self.username," ".join(parts)))
                    # See if we can handle it internally
                    try:
                        func = getattr(self, "command%s" % command.title())
                    except AttributeError:
                        # Can we find it from a plugin?
                        try:
                            func = self.commands[command.lower()]
                        except KeyError:
                            self.sendErrorMessage("Unknown command '%s'" % command)
                            return
                    if (self.isSpectator() and not self.isDirectorPlus() and (getattr(func, "admin_only", False) or getattr(func, "mod_only", False) or getattr(func, "op_only", False) or getattr(func, "member_only", False) or getattr(func, "worldowner_only", False) or getattr(func, "builder_only", False))):
                        self.sendServerMessage("'%s' is not available to specs." % command)
                        return
                    if getattr(func, "owner_only", False) and not self.isServerOwner():
                        self.sendServerMessage("'%s' is a Owner+ command!" % command)
                        return
                    if getattr(func, "director_only", False) and not self.isDirectorPlus():
                        self.sendServerMessage("'%s' is a Director+ command!" % command)
                        return
                    if getattr(func, "coder_only", False) and not self.isCoderPlus():
                        self.sendServerMessage("'%s' is an Admin+ command!" % command)
                        return
                    if getattr(func, "admin_only", False) and not self.isAdminPlus():
                        self.sendServerMessage("'%s' is an Admin+ command!" % command)
                        return
                    if getattr(func, "mod_only", False) and not self.isModPlus():
                        self.sendServerMessage("'%s' is a Mod+ command!" % command)
                        return
                    if getattr(func, "worldowner_only", False) and not self.isWorldOwnerPlus():
                        self.sendServerMessage("'%s' is a WorldOwner+ command!" % command)
                        return
                    if getattr(func, "op_only", False) and not self.isOpPlus():
                        self.sendServerMessage("'%s' is an Op+ command!" % command)
                        return
                    if getattr(func, "builder_only", False) and not self.isBuilderPlus():
                        self.sendServerMessage("'%s' is a Builder+ command!" % command)
                        return
                    if getattr(func, "member_only", False) and not (self.isMember() or self.isBuilderPlus()):
                        self.sendServerMessage("'%s' is a Member+ command!" % command)
                        return
                    if getattr(func, "unsilenced_only", False) and self.isSilenced():
                        self.sendServerMessage("Cat got your tongue?")
                        return
                    try:
                        func(parts, 'user', False) # fromloc is user, overriderank is false
                    except Exception, e:
                        self.sendSplitServerMessage(traceback.format_exc().replace("Traceback (most recent call last):", ""))
                        self.sendSplitServerMessage("Internal Server Error - Traceback (Please report this to the Server Staff or the iCraft Team, see /about for contact info)")
                        self.logger.error(traceback.format_exc())
                else:
                    # Everything else is a chat message of some kind.
                    # Note: Silence now overrides ALL forms of chat.
                    if message.startswith("@"):
                        # It's a whisper
                        try:
                            username, text = message[1:].strip().split(" ", 1)
                        except ValueError:
                            self.sendServerMessage("Please include a username and a message to send.")
                        else:
                            username = username.lower()
                            if username in self.factory.usernames:
                                self.factory.usernames[username].sendWhisper(self.username, text)
                                self.sendWhisper(self.username, text)
                                self.logger.info("@"+self.username+" (from "+self.username+"): "+text)
                                self.whisperlog.write("["+datetime.datetime.utcnow().strftime("%Y/%m/%d %H:%M:%S")+"] @"+self.username+" to "+username+": "+text+"\n")
                                self.whisperlog.flush()
                            else:
                                self.sendServerMessage("%s is currently offline." % username)
                    elif self.isSilenced():
                        self.sendServerMessage("Cat got your tongue?")
                    elif message.startswith("!"):
                        # It's a world message.
                        if len(message) == 1:
                            self.sendServerMessage("Please include a message to send.")
                        else:
                            try:
                                text = message[1:]
                            except ValueError:
                                self.sendServerMessage("Please include a message to send.")
                            else:
                                usertitlename = self.getUserTitleName()
                                self.sendWorldMessage ("!"+self.userColour()+usertitlename+":"+COLOUR_WHITE+" "+text)
                                self.logger.info("!"+usertitlename+" in "+str(self.world.id)+": "+text)
                                self.wclog.write("["+datetime.datetime.utcnow().strftime("%Y/%m/%d %H:%M:%S")+"] !"+usertitlename+" in "+str(self.world.id)+": "+text+"\n")
                                self.wclog.flush()
                                if self.factory.irc_relay:
                                    self.factory.irc_relay.sendServerMessage(COLOUR_YELLOW+"!"+self.userColour()+usertitlename+COLOUR_BLACK+" in "+str(self.world.id)+": "+text)
                    elif message.startswith("#"):
                        # It's a staff-only message.
                        if len(message) == 1:
                            self.sendServerMessage("Please include a message to send.")
                        else:
                            try:
                                text = message[1:]
                            except ValueError:
                                if self.isModPlus():
                                    self.sendServerMessage("Please include a message to send.")
                                else:
                                    self.factory.queue.put((self, TASK_MESSAGE, (self.id, self.userColour(), self.username, message)))
                            if self.isVisibleStaff():
                                self.factory.queue.put((self, TASK_STAFFMESSAGE, (0, self.userColour(), self.username, text, True)))
                            elif self.isHidden():
                                self.factory.queue.put((self, TASK_STAFFMESSAGE, (0, COLOUR_WHITE, "[Hidden]", text, False)))
                            else:
                                self.factory.queue.put((self, TASK_MESSAGE, (self.id, self.userColour(), self.getUserTitleName(), message)))
                    elif message.startswith("$"):
                        # It's an director-only message.
                        if len(message) == 1:
                            self.sendServerMessage("Please include a message to send.")
                        else:
                            try:
                                text = message[1:]
                            except ValueError:
                                if self.isDirectorPlus():
                                    self.sendServerMessage("Please include a message to send.")
                                else:
                                    self.factory.queue.put((self, TASK_MESSAGE, (self.id, self.userColour(), self.username, message)))
                            if self.isDirector() or self.isServerOwner():
                                self.factory.queue.put((self, TASK_DIRECTORMESSAGE, (0, self.userColour(), self.username, text, False)))
                            elif self.isHidden():
                                self.factory.queue.put((self, TASK_DIRECTORMESSAGE, (0, COLOUR_WHITE, "[Hidden]", text, False)))
                            else:
                                self.factory.queue.put((self, TASK_MESSAGE, (self.id, self.userColour(), self.getUserTitleName(), message)))
                    elif message.startswith("-"):
                        # It's a non-admin staff message.
                        if len(message) == 1:
                            self.sendServerMessage("Please include a message to send.")
                        else:
                            try:
                                text = message[1:]
                            except ValueError:
                                if self.isMod() or self.isDirectorPlus():
                                    self.sendServerMessage("Please include a message to send.")
                                else:
                                    self.factory.queue.put((self, TASK_MESSAGE, (self.id, self.userColour(), self.username, message)))
                            if self.isMod() or self.isDirector() or self.isServerOwner():
                                self.factory.queue.put((self, TASK_MODMESSAGE, (0, self.userColour(), self.username, text, False)))
                            elif self.isHidden():
                                self.factory.queue.put((self, TASK_MODMESSAGE, (0, COLOUR_WHITE, "[Hidden]", text, False)))
                            else:
                                self.factory.queue.put((self, TASK_MESSAGE, (self.id, self.userColour(), self.getUserTitleName(), message)))
                    elif message.startswith("+"):
                        # It's an admin+ staff message.
                        if len(message) == 1:
                            self.sendServerMessage("Please include a message to send.")
                        else:
                            try:
                                text = message[1:]
                            except ValueError:
                                if self.isAdminPlus():
                                    self.sendServerMessage("Please include a message to send.")
                                else:
                                    self.factory.queue.put((self, TASK_MESSAGE, (self.id, self.userColour(), self.username, message)))
                            if self.isAdmin() or self.isCoder() or self.isDirector() or self.isServerOwner():
                                self.factory.queue.put((self, TASK_ADMINCHATMESSAGE, (0, self.userColour(), self.username, text, False)))
                            elif self.isHidden():
                                self.factory.queue.put((self, TASK_ADMINCHATMESSAGE, (0, COLOUR_WHITE, "[Hidden]", text, False)))
                            else:
                                self.factory.queue.put((self, TASK_MESSAGE, (self.id, self.userColour(), self.getUserTitleName(), message)))
                    elif message.startswith("="):
                        # It's a coder+ staff message.
                        if len(message) == 1:
                            self.sendServerMessage("Please include a message to send.")
                        else:
                            try:
                                text = message[1:]
                            except ValueError:
                                if self.isCoderPlus():
                                    self.sendServerMessage("Please include a message to send.")
                                else:
                                    self.factory.queue.put((self, TASK_MESSAGE, (self.id, self.userColour(), self.username, message)))
                            if self.isCoder() or self.isDirector() or self.isServerOwner():
                                self.factory.queue.put((self, TASK_CODERMESSAGE, (0, self.userColour(), self.username, text, False)))
                            elif self.isHidden():
                                self.factory.queue.put((self, TASK_CODERMESSAGE, (0, COLOUR_WHITE, "[Hidden]", text, False)))
                            else:
                                self.factory.queue.put((self, TASK_MESSAGE, (self.id, self.userColour(), self.getUserTitleName(), message)))
                    else:
                        if override is not True:
                            self.factory.queue.put((self, TASK_MESSAGE, (self.id, self.userColour(), self.getUserTitleName(), message)))
                self.resetIdleTimer()
            else:
                if type == 2:
                    logging.logger.warn("Alpha Client Attempted to Connect.")
                    self.sendPacked(255, self.packString("Sorry, but this server only works for Classic."))
                    self.transport.loseConnection()
                else:
                    self.logger.warn("Unhandleable type %s" % type)
                    
    def getUserTitleName(self):
        rank = self.loadRank()      #TODO Fish - change this so we don't need to re-parse the title data for every message
        nameLower = self.username.lower()
        if nameLower in rank:
            title = rank[nameLower]+" "
        else:
            title = ""
        if len(title) > 0:
            if len(title) > 1 and title[len(title)-2] == "&":    # don't allow colors codes at the end of titles to have any affect
                return title[0:len(title)-2] + self.userColour() + self.username
            else:
                return title + self.userColour() + self.username
        else:
            return self.username
                    
    def userColour(self):
        if self.factory.colors:
            if (self.username.lower() in self.factory.spectators):
                color = COLOUR_BLACK
            elif (self.username.lower() in self.factory.owner):
                color = COLOUR_DARKRED
            elif (self.username.lower() in self.factory.directors):
                color = COLOUR_GREEN
            elif (self.username.lower() in self.factory.coders):
                color = COLOUR_DARKPURPLE
            elif (self.username.lower() in self.factory.admins):
                color = COLOUR_RED
            elif (self.username.lower() in self.factory.mods):
                color = COLOUR_BLUE
            elif self.username.lower() in INFO_VIPLIST:
                color = COLOUR_YELLOW
            elif (self.username.lower() in self.world.owner):
                color = COLOUR_DARKYELLOW
            elif (self.username.lower() in self.world.ops):
                color = COLOUR_DARKCYAN
            elif (self.username.lower() in self.world.builders):
                color = COLOUR_CYAN
            elif (self.username.lower() in self.factory.members):
                color = COLOUR_GREY
            else:
                color = COLOUR_WHITE
        else:
            color = COLOUR_WHITE
        return color

    def loadRank(self):
        file = open('config/data/titles.dat', 'r')
        bank_dic = cPickle.load(file)
        file.close()
        return bank_dic

    def colouredUsername(self):
        return self.userColour() + self.username

    def teleportTo(self, x, y, z, h=0, p=0):
        "Teleports the client to the coordinates"
        if h > 255:
            h = 255
        self.sendPacked(TYPE_PLAYERPOS, 255, (x<<5)+16, (y<<5)+16, (z<<5)+16, h, p)

    def changeToWorld(self, world_id, position=None):
        self.factory.queue.put((self, TASK_WORLDCHANGE, (self.id, self.world)))
        self.loading_world = True
        world = self.factory.joinWorld(world_id, self)
        self.runHook("newworld", world)
        if not self.isOpPlus():         #TODO Fish: what is this for and why isn't Builder involved?
            self.block_overrides = {}
        self.last_block_changes = []
        self.initial_position = position
        if self.world.is_archive:
            self.sendSplitServerMessage("This world is an Archive, and will cease to exist once the last person leaves.")
            self.sendServerMessage(COLOUR_RED+"Staff: Please do not reboot this world.")
        breakable_admins = self.runHook("canbreakadmin")
        self.sendPacked(TYPE_INITIAL, 7, ("%s: %s" % (self.factory.server_name, world_id)), "Entering world '%s'" % world_id, 100 if breakable_admins else 0)
        self.sendLevel()

    def sendOpUpdate(self):
        "Sends the admincrete-breaker update and a message."
        if self.isOp():
            self.sendServerMessage("You've been promoted to Op!")
        else:
            self.sendServerMessage("You've been demoted from Op!")
        self.runHook("rankchange")
        self.respawn()

    def sendWorldOwnerUpdate(self):
        "Sends the admincrete-breaker update and a message."
        if self.isWorldOwner():
            self.sendServerMessage("You've gained ownership of this world.")
        else:
            self.sendServerMessage("You've lost ownership of this world.")
        self.runHook("rankchange")
        self.respawn()

    def sendHiddenUpdate(self):
        "Sends the hidden update and a message."
        if self.isHidden():
            self.sendServerMessage("You've been promoted to Hidden!")
        else:
            self.sendServerMessage("You've been demoted from Hidden!")
        self.runHook("rankchange")
        self.respawn()

    def sendDirectorUpdate(self):
        "Sends the admincrete-breaker update and a message."
        if self.isDirector():
            self.sendServerMessage("You've been promoted to Director!")
        else:
            self.sendServerMessage("You've been demoted from Director!")
        self.runHook("rankchange")
        self.respawn()

    def sendCoderUpdate(self):
        "Sends the admincrete-breaker update and a message."
        if self.isCoder():
            self.sendServerMessage("You've been promoted to Coder!")
        else:
            self.sendServerMessage("You've been demoted from Coder!")
        self.runHook("rankchange")
        self.respawn()

    def sendAdminUpdate(self):
        "Sends the admincrete-breaker update and a message."
        if self.isAdmin():
            self.sendServerMessage("You've been promoted to Admin!")
        else:
            self.sendServerMessage("You've been demoted from Admin!")
        self.runHook("rankchange")
        self.respawn()

    def sendModUpdate(self):
        "Sends the mod message"
        if self.isMod():
            self.sendServerMessage("You've been promoted to Mod!")
        else:
            self.sendServerMessage("You've been demoted from Mod!")
        self.runHook("rankchange")
        self.respawn()

    def sendMemberUpdate(self):
        "Sends the member message"
        if self.isMember():
            self.sendServerMessage("You've been promoted to Member!")
        else:
            self.sendServerMessage("You've been demoted from Member!")
        self.runHook("rankchange")
        self.respawn()

    def sendSpectatorUpdate(self):
        "Sends a spec demotion message"
        self.runHook("rankchange")
        self.respawn()

    def sendBuilderUpdate(self):
        "Sends a message."
        if self.isBuilder():
            self.sendServerMessage("You've been promoted to Builder!")
        else:
            self.sendServerMessage("You've been demoted from Builder!")
        self.runHook("rankchange")
        self.respawn()

    def sendGlobalBuilderUpdate(self):
        "Sends a message."
        if self.isBuilder() and not self.isMember():        #TODO Fish: this probably isn't correct, but I don't haven't figured out globalbuilder yet
            self.sendServerMessage("You've been promoted to Global Builder!")
        else:
            self.sendServerMessage("You've been demoted from Global Builder!")
        self.runHook("rankchange")
        self.respawn()

    def respawn(self):
        "Respawns the user in-place for other users, updating their nick."
        self.queueTask(TASK_PLAYERRESPAWN, [self.id, self.colouredUsername(), self.x, self.y, self.z, self.h, self.p])

    def sendBlock(self, x, y, z, block=None):
        try:
            def real_send(block):
                self.sendPacked(TYPE_BLOCKSET, x, y, z, block)
            if block is not None:
                real_send(block)
            else:
                self.world[x, y, z].addCallback(real_send)
        except AssertionError:
            self.logger.warn("Block out of range: %s %s %s" % (x, y, z))

    def sendPlayerPos(self, id, x, y, z, h, p):
        self.sendPacked(TYPE_PLAYERPOS, id, x, y, z, h, p)

    def sendPlayerDir(self, id, h, p):
        self.sendPacked(TYPE_PLAYERDIR, id, h, p)

    def sendMessage(self, id, colour, username, text, direct=False, action=False):
        "Sends a message to the user, splitting it up if needed."
        # See if it's muted.
        replacement = self.runHook("recvmessage", colour, username, text, action)
        if replacement is False:
            return
        # See if we should highlight the names
        if action:
            prefix = "%s* %s%s%s " % (COLOUR_YELLOW, colour, username, COLOUR_WHITE)
        else:
            prefix = "%s%s:%s " % (colour, username, COLOUR_WHITE)
        # Send the message in more than one bit if needed
        self._sendMessage(prefix, text, id)

    def _sendMessage(self, prefix, message, id=127):
        "Utility function for sending messages, which does line splitting."
        lines = []
        temp = []
        thisline = ""
        words = message.split()
        linelen = 63 - len(prefix)
        for x in words:
            if len(thisline + " " + x) < linelen:
                thisline = thisline + " " + x
            else:
                if len(x) > linelen:
                    if not thisline == "":
                        lines.append(thisline)
                    while len(x) > linelen:
                        temp.append(x[:linelen])
                        x=x[linelen:]
                    lines = lines + temp
                    thisline = x
                else:
                    lines.append(thisline)
                    thisline = x
        if thisline != "":
            lines.append(thisline)
        for line in lines:
            if len(line) > 0:
                if line[0] == " ":
                    newline = line[1:]
                else:
                    newline = line
                if newline[len(newline)-2] == "&":
                    newline = newline[:len(newline)-2]
                self.sendPacked(TYPE_MESSAGE, id, prefix + newline)

    def sendAction(self, id, colour, username, text):
        self.sendMessage(id, colour, username, text, action=True)

    def sendWhisper(self, username, text):
        self.sendNormalMessage("%s@%s%s: %s%s" % (COLOUR_YELLOW, self.userColour(), username, COLOUR_WHITE, text))

    def sendServerMessage(self, message):
        self.sendPacked(TYPE_MESSAGE, 255, message)

    def sendErrorMessage(self, message):
        self.sendPacked(TYPE_MESSAGE, 255, "[!] "+COLOUR_RED+message)

    def sendNormalMessage(self, message):
        self._sendMessage("", message)

    def sendServerList(self, items, wrap_at=63, colors=True):
        "Sends the items as server messages, wrapping them correctly."
        current_line = items[0]
        for item in items[1:]:
            if len(current_line) + len(item) + 1 > wrap_at:
                if not colors:
                    self.sendNormalMessage(current_line)
                else:
                    self.sendServerMessage(current_line)
                current_line = item
            else:
                current_line += " " + item
        if not colors:
            self.sendNormalMessage(current_line)
        else:
            self.sendServerMessage(current_line)
            
    def sendServerPagedList(self, listTitle, items, page):
        numperpage = 50
        startindex = numperpage * (page-1)
        totalpages = int(math.ceil(len(items)/float(numperpage)))
        if page <= 0 or startindex >= len(items):
            self.sendServerMessage("There are only %s pages in the list." % totalpages)
        else:
            displaylist = items[startindex : startindex + numperpage]
            self.sendServerList([listTitle] + displaylist)
            self.sendServerMessage("Page %s of %s" % (page, totalpages))

    def sendSplitServerMessage(self, message):
        linelen = 63
        lines = []
        thisline = ""
        words = message.split()
        for x in words:
            if len(thisline + " " + x) < linelen:
                thisline = thisline + " " + x
            else:
                lines.append(thisline)
                thisline = x
        if thisline != "":
            lines.append(thisline)
        for line in lines:
            self.sendServerMessage(line)

    def splitMessage(self, message, linelen=63):
        lines = []
        thisline = ""
        words = message.split()
        for x in words:
            if len(thisline + " " + x) < linelen:
                thisline = thisline + " " + x
            else:
                lines.append(thisline)
                thisline = x
        if thisline != "":
            lines.append(thisline)
        return lines

    def sendNewPlayer(self, id, username, x, y, z, h, p):
        self.sendPacked(TYPE_SPAWNPOINT, id, username, x, y, z, h, p)

    def sendPlayerLeave(self, id,):
        self.sendPacked(TYPE_PLAYERLEAVE, id)

    def sendKeepAlive(self):
        if self.connected:
            self.sendPacked(TYPE_KEEPALIVE)
            reactor.callLater(1, self.sendKeepAlive)

    def sendOverload(self):
        "Sends an overload - a fake world designed to use as much memory as it can."
        self.sendPacked(TYPE_INITIAL, 7, "Loading...", "Entering world 'default'...", 0)
        self.sendPacked(TYPE_PRECHUNK)
        reactor.callLater(0.001, self.sendOverloadChunk)

    def sendOverloadChunk(self):
        "Sends a level chunk full of 1s."
        if self.connected:
            self.sendPacked(TYPE_CHUNK, 1024, "\1"*1024, 50)
            reactor.callLater(0.001, self.sendOverloadChunk)

    def sendLevel(self, slient=False):
        "Starts the process of sending a level to the client."
        self.factory.recordPresence(self.username)
        self.sendLevelSlient = slient
        # Ask the World to flush the level and get a gzip handle back to us.
        if hasattr(self, "world"):
            self.world.get_gzip_handle().addCallback(self.sendLevelStart)

    def sendLevelStart(self, (gzip_handle, zipped_size)):
        "Called when the world is flushed and the gzip is ready to read."
        # Store that handle and size
        self.zipped_level, self.zipped_size = gzip_handle, zipped_size
        # Preload our first chunk, send a level stream header, and go!
        self.chunk = self.zipped_level.read(1024)
        self.logger.debug("Sending level...")
        self.sendPacked(TYPE_PRECHUNK)
        reactor.callLater(0.001, self.sendLevelChunk)

    def sendLevelChunk(self):
        if not hasattr(self, 'chunk'):
            self.logger.error("Cannot send chunk, there isn't one! %r %r" % (self, self.__dict__))
            return
        if self.chunk:
            self.sendPacked(TYPE_CHUNK, len(self.chunk), self.chunk, chr(int(100*(self.zipped_level.tell()/float(self.zipped_size)))))
            self.chunk = self.zipped_level.read(1024)
            reactor.callLater(0.001, self.sendLevelChunk)
        else:
            self.zipped_level.close()
            del self.zipped_level
            del self.chunk
            del self.zipped_size
            self.endSendLevel()

    def endSendLevel(self):
        self.logger.debug("Sent level data.")
        self.sendPacked(TYPE_LEVELSIZE, self.world.x, self.world.y, self.world.z)
        sx, sy, sz, sh = self.world.spawn
        self.p = 0
        self.loading_world = False
        # If we have a custom point set (teleport, tp), use that
        if self.initial_position:
            try:
                sx, sy, sz, sh = self.initial_position
            except ValueError:
                sx, sy, sz = self.initial_position
                sh = 0
            self.initial_position = None
        self.x = (sx<<5)+16
        self.y = (sy<<5)+16
        self.z = (sz<<5)+16
        self.h = int(sh*255/360.0)
        self.sendPacked(TYPE_SPAWNPOINT, chr(255), "", self.x, self.y, self.z, self.h, 0)
        self.sendAllNew()
        self.factory.queue.put((self, TASK_NEWPLAYER, (self.id, self.colouredUsername(), self.x, self.y, self.z, self.h, 0)))
        if not self.sendLevelSlient:
            self.sendWelcome()
        del self.sendLevelSlient

    def sendAllNew(self):
        "Sends a 'new user' notification for each new user in the world."
        for client in self.world.clients:
            if client is not self and hasattr(client, "x"):
                self.sendNewPlayer(client.id, client.userColour() + client.username, client.x, client.y, client.z, client.h, client.p)

    def sendWelcome(self):
        if not self.sent_first_welcome:
            try:
                r = open('config/greeting.txt', 'r')
            except:
                r = open('config/greeting.example.txt', 'r')
            for line in r:
                self.sendPacked(TYPE_MESSAGE, 127, line)
            self.sent_first_welcome = True
            self.runHook("playerjoined",self.username)
            self.MessageAlert()
        else:
            self.sendPacked(TYPE_MESSAGE, 255, "You are now in world '%s'" % self.world.id)

    def AllowedToBuild(self,x,y,z):
        build = False
        assigned = []
        try:
            check_offset = self.world.blockstore.get_offset(x, y, z)
            block = ord(self.world.blockstore.raw_blocks[check_offset])
        except:
            self.sendErrorMessage("Out of bounds.")
            return False
        if block == BLOCK_SOLID and not self.isOpPlus():
            return False
        for id, zone in self.world.userzones.items():
            x1, y1, z1, x2, y2, z2 = zone[1:7]
            if x1 < x < x2:
                if y1 < y < y2:
                    if z1 < z < z2:
                        if len(zone) > 7:
                            if self.username.lower() in zone[7:] or self.isDirectorPlus():
                                build = True
                            else:
                                assigned = zone[7:]
                        else:
                            return False
        if build:
            return True
        elif assigned:
            self.sendServerList(["You are not allowed to build in this zone. Only:"]+assigned+["may."])
            return False
        for id, zone in self.world.rankzones.items():
            if "all" == zone[7]:
                x1, y1, z1, x2, y2, z2 = zone[1:7]
                if x1 < x < x2:
                    if y1 < y < y2:
                        if z1 < z < z2:
                            return True
            if self.world.zoned:
                if "builder" == zone[7]:
                    x1, y1, z1, x2, y2, z2 = zone[1:7]
                    if x1 < x < x2:
                        if y1 < y < y2:
                            if z1 < z < z2:
                                if self.isBuilderPlus():
                                    return True
                                else:
                                    self.sendServerMessage("You must be "+zone[7]+" to build here.")
                                    return False
                if "op" == zone[7]:
                    x1, y1, z1, x2, y2, z2 = zone[1:7]
                    if x1 < x < x2:
                        if y1 < y < y2:
                            if z1 < z < z2:
                                if self.isOpPlus():
                                    return True
                                else:
                                    self.sendServerMessage("You must be "+zone[7]+" to build here.")
                                    return False
                if "worldowner" == zone[7]:
                    x1, y1, z1, x2, y2, z2 = zone[1:7]
                    if x1 < x < x2:
                        if y1 < y < y2:
                            if z1 < z < z2:
                                if self.isWorldOwnerPlus():
                                    return True
                                else:
                                    self.sendServerMessage("You must be "+zone[7]+" to build here.")
                                    return False
                if "member" == zone[7]:
                    x1, y1, z1, x2, y2, z2 = zone[1:7]
                    if x1 < x < x2:
                        if y1 < y < y2:
                            if z1 < z < z2:
                                if self.isMember() or self.isWorldOwnerPlus():
                                    return True
                                else:
                                    self.sendServerMessage("You must be "+zone[7]+" to build here.")
                                    return False
                if "mod" == zone[7]:
                    x1, y1, z1, x2, y2, z2 = zone[1:7]
                    if x1 < x < x2:
                        if y1 < y < y2:
                            if z1 < z < z2:
                                if self.isModPlus():
                                    return True
                                else:
                                    self.sendServerMessage("You must be "+zone[7]+" to build here.")
                                    return False
                if "admin" == zone[7]:
                    x1, y1, z1, x2, y2, z2 = zone[1:7]
                    if x1 < x < x2:
                        if y1 < y < y2:
                            if z1 < z < z2:
                                if self.isAdminPlus():
                                    return True
                                else:
                                    self.sendServerMessage("You must be "+zone[7]+" to build here.")
                                    return False
                if "coder" == zone[7]:
                    x1, y1, z1, x2, y2, z2 = zone[1:7]
                    if x1 < x < x2:
                        if y1 < y < y2:
                            if z1 < z < z2:
                                if self.isCoderPlus():
                                    return True
                                else:
                                    self.sendServerMessage("You must be "+zone[7]+" to build here.")
                                    return False
                if "director" == zone[7]:
                    x1, y1, z1, x2, y2, z2 = zone[1:7]
                    if x1 < x < x2:
                        if y1 < y < y2:
                            if z1 < z < z2:
                                if self.isDirectorPlus():
                                    return True
                                else:
                                    self.sendServerMessage("You must be "+zone[7]+" to build here.")
                                    return False
                if "owner" == zone[7]:
                    x1, y1, z1, x2, y2, z2 = zone[1:7]
                    if x1 < x < x2:
                        if y1 < y < y2:
                            if z1 < z < z2:
                                if self.isServerOwner():
                                    return True
                                else:
                                    self.sendServerMessage("You must be "+zone[7]+" to build here.")
                                    return False
        if self.world.all_write:
            return True
        if not self.world.all_write and self.isBuilderPlus():
            return True
        if self.world.id == self.factory.default_name and self.isMember() and not self.isModPlus() and not self.world.all_write:
            self.sendBlock(x, y, z)     #TODO Fish: what is this doing that all the rest of the code here wouldn't accomplish?
            self.sendServerMessage("Only Builder/Op and Mod+ may edit '%s'." % self.factory.default_name)
            return      #TODO Fish: and why isn't this returning a value?
        self.sendErrorMessage("This world is locked. You must be Builder+ to build here.")
        return False

    def GetBlockValue(self, value):
        # Try getting the block as a direct integer type.
        try:
            block = chr(int(value))
        except ValueError:
            # OK, try a symbolic type.
            try:
                block = chr(globals()['BLOCK_%s' % value.upper()])
            except KeyError:
                self.sendErrorMessage("'%s' is not a valid block type." % value)
                return None
                    # Check the block is valid
        if ord(block) > 49:
            self.sendErrorMessage("'%s' is not a valid block type." % value)
            return None
        op_blocks = [BLOCK_SOLID, BLOCK_WATER, BLOCK_LAVA]
        if ord(block) in op_blocks and not self.isOpPlus():
            self.sendErrorMessage("Sorry, but you can't use that block.")
            return
        return block

    def MessageAlert(self):
        if os.path.exists("config/data/inbox.dat"):
            file = open('config/data/inbox.dat', 'r')
            messages = cPickle.load(file)
            file.close()
            for client in self.factory.clients.values():
                if client.username in messages:
                    client.sendServerMessage("You have a message waiting in your Inbox.")
                    client.sendServerMessage("Use /inbox to check and see.")
                    reactor.callLater(300, self.MessageAlert)

    def announceGlobal(self, actionType, targetUsername, reason=""):
        if self.isOnlyHiddenNotVisibleStaff():
            self.factory.announceGlobal(actionType, "", targetUsername, reason)
        else:
            self.factory.announceGlobal(actionType, self.username, targetUsername, reason)

    # This will disconnect the client with a message generated from the other parameters.
    # invokerClient is only needed if you want the message to contain the name of the user that invoked the action, otherwise it can be None.
    # invokerName is used to provide a name string if you don't have a client object (such as with IRC).
    def sendErrorAction(self, actionType, invokerClient, reason="", invokerName=""):
        if actionType == ACTION_KICK:
            action = "kicked"
        elif actionType == ACTION_BAN:
            action = "banned"
        elif actionType == ACTION_IPBAN:
            action = "banned"   # lie and say it's a normal ban. no reason to give them any hints
        msg = "You were " + action
        if len(invokerName) > 0:
            msg += " by " + invokerName
        elif invokerClient and invokerClient.isOnlyHiddenNotVisibleStaff():
            msg += " by " + invokerClient.username
        msg += "."
        if len(reason) > 0:
            msg += " Reason: " + reason
        self.sendError(msg)

    def getCommandFunc(self, commandName):
        # Try looking up the command on this CoreServerProtocol object first.
        #func = getattr(self, "command%s" % commandName.title())
        #if func is None:
        # Try to find it in a plugin.
        func = self.commands.get(commandName.lower())
        return func
