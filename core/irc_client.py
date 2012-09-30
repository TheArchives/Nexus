# The Nexus software is licensed under the BSD 2-Clause license.
#
# You should have recieved a copy of this license with the software.
# If you did not, you can find one at the following link.
#
# http://opensource.org/licenses/bsd-license.php

import datetime, traceback, logging, math, random, time
from reqs.twisted.words.protocols import irc
from reqs.twisted.words.protocols.irc import IRC
from reqs.twisted.internet import protocol
from core.constants import *
from core.globals import *
from core.plugins import protocol_plugins
from core.decorators import *

class ChannelUserData():
    def __init__(self):
        self.ops = set()
        self.voice = set()
        self.all = set()
        
    def removeUser(self, username):
        self.ops.discard(username)
        self.voice.discard(username)
        self.all.discard(username)
        
    def renameUser(self, oldname, newname):
        if oldname in self.ops:
            self.ops.remove(oldname)
            self.ops.add(newname)
        if oldname in self.voice:
            self.voice.remove(oldname)
            self.voice.add(newname)
        if oldname in self.all:
            self.all.remove(oldname)
            self.all.add(newname)

class ChatBot(irc.IRCClient):
    """An IRC-server chat integration bot."""
    
    ocommands = ["help", "cmdlist", "banreason", "kick", "ban", "unban", "shutdown", "spec", "boot", "showops", "showvoices"]
    ncommands = ["who", "worlds", "staff", "credits", "help", "rules", "cmdlist", "about", "lastseen", "roll"]

    def kickedFrom(self, channel, kicker, message):
        self.join(self.factory.irc_channel)
        self.msg(self.factory.irc_channel, "You failed, %s!" % kicker)

    def connectionMade(self):
        self.logger = logging.getLogger("IRC Bot")
        self.users = {}     # this will be a Dictionary with Keys being channel names and each Value being a ChannelUserData
        self.nickname = self.factory.main_factory.irc_nick
        self.password = self.factory.main_factory.irc_pass
        self.prefix = "none"
        irc.IRCClient.connectionMade(self)
        self.factory.instance = self
        self.factory, self.controller_factory = self.factory.main_factory, self.factory
        self.world = None
        self.sendLine('NAMES ' + self.factory.irc_channel)
        self.sendLine('NAMES ' + self.factory.staffchat_channel)

    def connectionLost(self, reason):
        irc.IRCClient.connectionLost(self, reason)
        self.logger.info("IRC client disconnected. (%s)" % reason)

    # callbacks for events

    def ctcpQuery_VERSION(self, user, channel, data):
        """Called when received a CTCP VERSION request."""
        nick = user.split("!")[0]
        self.ctcpMakeReply(nick, [('VERSION', 'Nexus %s - a Minecraft server written in Python.' % VERSION)])

    def signedOn(self):
        """Called when bot has succesfully signed on to server."""
        self.logger.info("IRC client connected.")
        self.msg("NickServ", "IDENTIFY %s" % self.password)
        self.msg("ChanServ", "INVITE %s" % self.factory.irc_channel)
        self.join(self.factory.irc_channel)
        self.msg("ChanServ", "INVITE %s" % self.factory.staffchat_channel)
        self.join(self.factory.staffchat_channel)

    def joined(self, channel):
        """This will get called when the bot joins the channel."""
        self.users[channel.lower()] = ChannelUserData()            # this should initialize all the needed entries in the dictionary so that we don't have to worry about that part anywhere else
        self.logger.info("IRC client joined %s." % channel)

    def sendError(self, error):
        self.logger.error("Sending error: %s" % error)
        self.sendPacked(TYPE_ERROR, error)
        reactor.callLater(0.2, self.transport.loseConnection)

    def lineReceived(self, line): # use instead of query
        line = irc.lowDequote(line)
        try:
            prefix, command, params = irc.parsemsg(line)
            if irc.numeric_to_symbolic.has_key(command):
                command = irc.numeric_to_symbolic[command]
            self.handleCommand(command, prefix, params)
        except irc.IRCBadMessage:
            self.badMessage(line, *sys.exc_info())
        try:
            if command == "RPL_NAMREPLY":
                names = params[3].split()
                for name in names:
                    if name.startswith("@"):
                        actual_name = name[1:]
                        self.users[params[2].lower()].ops.add(actual_name)
                    elif name.startswith("+"):
                        actual_name = name[1:]
                        self.users[params[2].lower()].voice.add(actual_name)
                    else:
                        actual_name = name
                    self.users[params[2].lower()].all.add(actual_name)
        except:
            self.logger.error(traceback.format_exc())

    def AdminCommand(self, command):
        try:
            user = command[0]
            if self.userHasVoicePlus(user):
                if len(command) > 1:
                    if command[1].startswith("#"):
                        if self.factory.staffchat and not command[0]==self.nickname:
                            # It's an staff-only message.
                            if len(command[1]) == 1:
                                self.msg(user, "07Please include a message to send.")
                            else:
                                try:
                                    text = " ".join(command[1:])[1:]
                                except ValueError:
                                    self.factory.queue.put((self, TASK_MESSAGE, (0, COLOUR_DARKGREEN, "Console", message)))
                                else:
                                    self.factory.queue.put((self, TASK_STAFFMESSAGE, (0, COLOUR_PURPLE, command[0],text,True)))
                                    self.adlog = open("logs/server.log", "a")
                                    self.adlog = open("logs/world.log", "a")
                                    self.adlog.write(datetime.datetime.utcnow().strftime("%Y/%m/%d %H:%M:%S")+" | #" + command[0] + ": "+text+"\n")
                                    self.adlog.flush()
                    elif command[1] in self.ocommands and len(command) > 1:
                        if command[1] == ("help"):
                            self.msg(user, "07Staff Help")
                            self.msg(user, "07Commands: Use 'cmdlist'")
                            if self.factory.staffchat:
                                self.msg(user, "07StaffChat: Use '#message'")
                        elif command[1] == ("cmdlist"):
                            self.msg(user, "07Here are your Admin Commands:")
                            self.msg(user, "07ban banned banreason boot derank kick rank shutdown spec")
                            self.msg(user, "07Use 'command arguments' to do it.")
                        elif command[1] == ("banreason"):
                            if len(command) == 3:
                                username = command[2]
                                if not self.factory.isBanned(username):
                                    self.msg(user,"07%s is not Banned." % username)
                                else:
                                    self.msg(user,"07Reason: %s" % self.factory.banReason(username))
                            else:
                                self.msg(user,"07You must provide a name.")
                        #elif command[1] == ("banned"):
                        #    self.msg(user,  ", ".join(self.factory.banned))
                        elif command[1] == ("kick"):
                            if command >= 3:
                                targetUser = command[2].lower()
                                for client in self.factory.clients.values():
                                    if client.username.lower() == targetUser:
                                        reason = " ".join(command[3:])
                                        client.sendErrorAction(ACTION_KICK, None, reason, user)
                                        self.msg(targetUser, "07"+str(command[2])+" has been kicked from the server.")
                                        client.factory.announceGlobal(ACTION_KICK, user, client.username, reason)
                                        return
                                self.msg(user, "07"+str(command[2])+" is not online.")
                            else:
                                self.msg(user,"07Please give a username.")
                        elif command[1] == ("ban"):
                            if self.userHasOps(user):
                                if command > 3:
                                    targetUser = command[2].lower()
                                    if self.factory.isBanned(targetUser):
                                        self.msg(user,"07%s is already Banned." % targetUser)
                                    else:
                                        reason = " ".join(command[3:])
                                        self.factory.addBan(targetUser, reason)
                                        if targetUser in self.factory.usernames:
                                            self.factory.usernames[targetUser].sendErrorAction(ACTION_BAN, None, reason, user)
                                        self.factory.announceGlobal(ACTION_BAN, user, targetUser, reason)
                                        self.msg(user,"07%s has been Banned for %s." % (targetUser, reason))
                                else:
                                    self.msg(user,"07Please give a username and reason.")
                            else:
                                self.msg(user,"07You must be an op to use this command!")
                        elif command[1] == ("unban"):
                            if self.userHasOps(user):
                                if command >= 3:
                                    targetUser = command[2].lower()
                                    if not self.factory.isBanned(targetUser):
                                        self.msg(user,"07%s is not banned." % targetUser)
                                    else:
                                        self.factory.removeBan(targetUser)
                                        self.factory.announceGlobal(ACTION_UNBAN, user, targetUser)
                                        self.msg(user,"07%s has been unbanned." % targetUser)
                                else:
                                    self.msg(user,"07Please give a username and reason.")
                            else:
                                self.msg(user,"07You must be an op to use this command!")
                        elif command[1] == ("shutdown"):
                            world = str(command[2]).lower()
                            if world in self.factory.worlds:
                                self.factory.unloadWorld(world)
                                self.msg(user,"07World '"+world+"' shutdown.")
                            else:
                                self.msg(user,"07World '"+world+"' is not loaded.")
                        # elif command[1] == ("rank"):
                            # if self.userHasOps(user):
                                # if not len(command) > 2:
                                    # self.msg(user, "07You must provide a username.")
                                # else:
                                    # self.msg(user,Rank(self, command[1:] + [user], False, True, self.factory))
                            # else:
                                # self.msg(user,"07You must be an op to use this command!")
                        # elif command[1] == ("derank"):
                            # if self.userHasOps(user):
                                # if not len(command) > 2:
                                    # self.msg(user, "07You must provide a username.")
                                # else:
                                    # self.msg(user,DeRank(self, command[1:] + [user], False, True, self.factory))
                            # else:
                                # self.msg(user,"07You must be an op to use this command!")
                        elif command[1] == ("spec"):
                            if not len(command) > 2:
                                self.msg(user, "07You must provide a username.")
                            else:
                                self.msg(user,Spec(self, command[1], False, True, self.factory))
                        elif command[1] == ("boot"):
                            world = str(command[2]).lower()
                            self.factory.loadWorld("worlds/"+world, world)
                            self.msg(user,"07World '"+world+"' booted.")
                        elif command[1] == ("showops"):
                            self.msg(user, "07This bot currently thinks the following are ops on IRC: " + ','.join(self.getOpList()))
                        elif command[1] == ("showvoices"):
                            self.msg(user, "07This bot currently thinks the following have voice on IRC: " + ','.join(self.getVoiceList()))
                        else:
                            self.msg(user, "07Sorry, "+command[1]+" is not a command!")
                    else:
                        self.msg(user, "07%s is not a command!" % command[1] )
                else:
                    self.msg(user,"07You must provide a valid command to use the IRC bot." )
            else:
                if command[1].startswith("#"):
                    if self.factory.staffchat:
                        self.msg(user, "07You must be an op to use StaffChat.")
                elif command[1] in self.ocommands:
                    self.msg(user, "07You must be an op to use %s." %command[1])
                else:
                    self.msg( user, "07%s is not a command!" % command[1] )
            if not command[1].startswith("#"):
                self.logger.info("%s just used: %s" % (user, " ".join(command[1:])))
        except:
            self.logger.error(traceback.format_exc())
            self.msg(user, "Internal Server Error (See the Console for more details)")

    def privmsg(self, user, channel, msg):
        """This will get called when the bot receives a message."""
        try:
            user = user.split('!', 1)[0]
            msg = "".join([char for char in msg if ord(char) < 128 and char != "" or "0"])
            if channel == self.nickname:
                if not ("Serv" in user):
                    msg_command = msg.split()
                    #if not(self.nickname == user):
                    self.AdminCommand([user] + msg_command)
            elif channel.lower() == self.factory.staffchat_channel.lower():
                if msg.startswith("#"):
                    # It's a staffchat message.
                    if self.factory.staffchat and not msg[0]==self.nickname and self.userHasVoicePlus(user):
                        # It's an staff-only message
                        if len(msg) == 1:
                            self.msg(self.factory.staffchat_channel, "07Please include a message to send.")
                        else:
                            self.factory.queue.put((self, TASK_IRCSTAFFMESSAGE, (0, COLOUR_PURPLE, user,msg[1:],True)))
                            self.adlog = open("logs/server.log", "a")
                            self.adlog = open("logs/world.log", "a")
                            self.adlog.write(datetime.datetime.utcnow().strftime("%Y/%m/%d %H:%M:%S")+" | #" + user +  ": "+msg[1:]+"\n")
                            self.adlog.flush()
            elif channel.lower() == self.factory.irc_channel.lower():
                if msg.lower().lstrip(self.nickname.lower()).startswith("$"+self.nickname.lower()):
                    msg_command = msg.split()
                    if len(msg_command) > 1:
                        if msg_command[1] in self.ncommands and len(msg_command) > 1:
                            if msg_command[1] == ("who"):
                                self.msg(self.factory.irc_channel, "07Who's Online?")
                                none = True
                                for key in self.factory.worlds:
                                    users =  ", ".join(str(c.username) for c in self.factory.worlds[key].clients)
                                    if users:
                                        whois = ("07%s: %s" % (key, users))
                                        self.msg(self.factory.irc_channel, whois)
                                        users = None
                                        none = False
                                if none:
                                    self.msg(self.factory.irc_channel, "07No users are online.")
                            elif msg_command[1] == ("worlds"):
                                self.msg(self.factory.irc_channel, "07Worlds Booted")
                                worlds = ", ".join([id for id, world in self.factory.worlds.items()])
                                self.msg(self.factory.irc_channel, "07Online Worlds: "+worlds)
                            elif msg_command[1] == ("staff"):
                                self.msg(self.factory.irc_channel,"07Please see your PM for the Staff List.")
                                self.msg(user, "The Server Staff - Owner: "+self.factory.owner)
                                list = Staff(self, self.factory)
                                for each in list:
                                    self.msg(user," ".join(each))
                            elif msg_command[1] == ("credits"):
                                self.msg(self.factory.irc_channel,"07Please see your PM for the Credits.")
                                self.msg(user, "The Credits")
                                list = Credits()
                                for each in list:
                                    self.msg(user,"".join(each))
                            elif msg_command[1] == ("help"):
                                self.msg(self.factory.irc_channel, "07Help Center")
                                self.msg(self.factory.irc_channel, "07Commands: Use '$"+self.nickname+" cmdlist'")
                                self.msg(self.factory.irc_channel, "07WorldChat: Use '!world message'")
                                self.msg(self.factory.irc_channel, "07IRCChat: Use '$message'")
                                self.msg(self.factory.irc_channel, "07About: Use '$"+self.nickname+" about'")
                                self.msg(self.factory.irc_channel, "07Credits: Use '$"+self.nickname+" credits'")
                            elif msg_command[1] == ("rules"):
                                self.msg(self.factory.irc_channel,"07Please see your PM for the Rules.")
                                self.msg(user, "The Rules")
                                try:
                                    r = open('config/rules.txt', 'r')
                                except:
                                    r = open('config/rules.example.txt', 'r')
                                for line in r:
                                    line = line.replace("\n", "")
                                    self.msg(user, line)
                            elif msg_command[1] == ("cmdlist"):
                                self.msg(self.factory.irc_channel, "07Command List")
                                self.msg(self.factory.irc_channel, "07about cmdlist credits help roll rules staff who worlds")
                                self.msg(self.factory.irc_channel, "07Use '$"+self.nickname+" command arguments' to do it.")
                                self.msg(self.factory.irc_channel, "07NOTE: Admin Commands are by PMing "+self.nickname+" - only for ops.")
                            elif msg_command[1] == ("about"):
                                self.msg(self.factory.irc_channel, "07About the Server, powered by iCraft+ %s | Credits: Use '$%s credits'" % (VERSION, self.nickname))
                                self.msg(self.factory.irc_channel, "07Name: "+self.factory.server_name+"; owned by "+self.factory.owner)
                                try:
                                    self.msg(self.factory.irc_channel, "07URL: "+self.factory.heartbeat.url)
                                except:
                                    self.msg(self.factory.irc_channel, "07URL: N/A (minecraft.net is offline)")
                                self.msg(self.factory.irc_channel, "07Site: "+self.factory.info_url)
                            elif msg_command[1] == "roll":
                                if len(msg_command) < 2:
                                    self.msg(self.factory.irc_channel, "07Please enter a number as the maximum roll.")
                                else:
                                    try:
                                        if int(msg_command[2])>100:
                                            msg_command[2]="100"
                                        roll = int(math.floor((random.random() * (int(msg_command[2]) - 1) + 1)))
                                    except ValueError:
                                        self.msg(self.factory.irc_channel, "07Please enter an integer as the maximum roll.")
                                    else:
                                        self.msg(self.factory.irc_channel, "07%s rolled a %s" % (user, roll))
                            elif msg_command[1] == "lastseen":
                                if len(msg_command) <2:
                                    self.msg(self.factory.irc_channel, "07Please enter a username to look for.")
                                else:
                                    if msg_command[2].lower() not in self.factory.lastseen:
                                        self.msg(self.factory.irc_channel, "07There are no records of %s." % msg_command[2])
                                    else:
                                        t = time.time() - self.factory.lastseen[msg_command[2].lower()]
                                        days = t // 86400
                                        hours = (t % 86400) // 3600
                                        mins = (t % 3600) // 60
                                        desc = "%id, %ih, %im" % (days, hours, mins)
                                        self.msg(self.factory.irc_channel, "07%s was last seen %s ago." % (msg_command[2], desc))
                            else:
                                self.msg(self.factory.irc_channel, "07Sorry, "+msg_command[1]+" is not a command!")
                            self.logger.info("%s just used: %s" % (user, " ".join(msg_command[1:])))
                        elif msg_command[1] in self.ocommands and len(msg_command) > 1:
                            if self.userHasOps(user):
                                self.msg(self.factory.irc_channel, "07Please do not use %s in the channel; use a query instead!" % msg_command[1])
                            else:
                                self.msg(self.factory.irc_channel, "07You must be an op to use %s." % msg_command[1]) 
                        else:
                            self.msg(self.factory.irc_channel,"07You must provide a valid command to use the IRC bot - try the help command.")
                    else:
                        self.msg(self.factory.irc_channel,"07You must provide a valid command to use the IRC bot - try the help command.")
                elif msg.startswith("$"):
                    self.logger.info("<$%s> %s" % (user, msg))
                elif msg.startswith("!"):
                    # It's a world message.
                    message = msg.split(" ")
                    if len(message) == 1:
                        self.msg(self.factory.irc_channel, "07Please include a message to send.")
                    else:
                        try:
                           world = message[0][1:len(message[0])]
                           out = "\n ".join(message[1:])
                           text = COLOUR_PURPLE+"IRC: "+COLOUR_WHITE+"<!"+user+">"+COLOUR_WHITE+out
                        except ValueError:
                            self.msg(self.factory.irc_channel, "07Please include a message to send.")
                        else:
                            if world in self.factory.worlds:
                                self.factory.queue.put((self.factory.worlds[world], TASK_WORLDMESSAGE, (255, self.factory.worlds[world], text),))
                                self.logger.debug("WORLD - "+user+" in "+str(self.factory.worlds[world].id)+": "+out)
                                self.wclog = open("logs/server.log", "a")
                                self.wclog.write(datetime.datetime.utcnow().strftime("%Y/%m/%d %H:%M:%S")+" | !"+user+" in "+str(self.factory.worlds[world].id)+": "+out+"\n")
                                self.wclog.flush()
                                self.wclog.close()
                            else:
                                self.msg(self.factory.irc_channel, "07That world does not exist. Try !world message")
                elif self.prefix == "none":
                    msg = msg.replace("0", "&f")
                    msg = msg.replace("00", "&f")
                    msg = msg.replace("1", "&0")
                    msg = msg.replace("01", "&0")
                    msg = msg.replace("2", "&1")
                    msg = msg.replace("02", "&1")
                    msg = msg.replace("3", "&2")
                    msg = msg.replace("03", "&2")
                    msg = msg.replace("4", "&c")
                    msg = msg.replace("04", "&c")
                    msg = msg.replace("5", "&4")
                    msg = msg.replace("05", "&4")
                    msg = msg.replace("6", "&5")
                    msg = msg.replace("06", "&5")
                    msg = msg.replace("7", "&6")
                    msg = msg.replace("07", "&6")
                    msg = msg.replace("8", "&e")
                    msg = msg.replace("08", "&e")
                    msg = msg.replace("9", "&a")
                    msg = msg.replace("09", "&a")
                    msg = msg.replace("10", "&3")
                    msg = msg.replace("11", "&b")
                    msg = msg.replace("12", "&9")
                    msg = msg.replace("13", "&d")
                    msg = msg.replace("14", "&8")
                    msg = msg.replace("15", "&7")
                    goodchars = ["a", "b", "c", "d", "e", "f", "g", "h", "i", "j", "k", "l", "m", "n", "o", "p", "q", "r", "s", "t", "u", "v", "w", "x", "y", "z", " ", "0", "1", "2", "3", "4", "5", "6", "7", "8", "9", " ", "!", "@", "#", "$", "%", "*", "(", ")", "-", "_", "+", "=", "{", "[", "}", "]", ":", ";", "\"", "\'", "<", ",", ">", ".", "?", "/", "\\", "|", "^", "~"]
                    for character in msg:
                        if not character.lower() in goodchars:
                            msg = msg.replace(character, "*")
                    msg = msg.replace("%0", "&0")
                    msg = msg.replace("%1", "&1")
                    msg = msg.replace("%2", "&2")
                    msg = msg.replace("%3", "&3")
                    msg = msg.replace("%4", "&4")
                    msg = msg.replace("%5", "&5")
                    msg = msg.replace("%6", "&6")
                    msg = msg.replace("%7", "&7")
                    msg = msg.replace("%8", "&8")
                    msg = msg.replace("%9", "&9")
                    msg = msg.replace("%a", "&a")
                    msg = msg.replace("%b", "&b")
                    msg = msg.replace("%c", "&c")
                    msg = msg.replace("%d", "&d")
                    msg = msg.replace("%e", "&e")
                    msg = msg.replace("%f", "&f")
                    msg = msg.replace("./", " /")
                    msg = msg.replace(".!", " !")
                    msg = msg.replace(".$", " $")
                    msg = msg.replace(".+", " +")
                    if msg[len(msg)-2] == "&":
                        self.msg(self.factory.irc_channel, "07You cannot use a color at the end of a message.")
                        return
                    if len(msg) > 51:
                        moddedmsg = msg[:51].replace(" ", "")
                        if moddedmsg[len(moddedmsg)-2] == "&":
                            msg = msg.replace("&", "*")
                    for client in self.factory.clients.values():
                        client.sendNormalMessage(COLOUR_WHITE+"[IRC] "+COLOUR_PURPLE+user+": "+COLOUR_WHITE+msg)
                    #self.factory.queue.put((self, TASK_IRCMESSAGE, (127, "[IRC] " + COLOUR_PURPLE, user, msg)))
                    self.logger.info("[IRC] <%s> %s" % (user, msg))
                    self.factory.chatlog.write("[%s] <*%s> %s\n" % (datetime.datetime.utcnow().strftime("%Y/%m/%d %H:%M:%S"), user, msg))
                    self.factory.chatlog.flush()
        except:
            self.logger.error(traceback.format_exc())
            self.msg(self.factory.irc_channel, "Internal Server Error (See the Console for more details)")

    def action(self, user, channel, msg):
        """This will get called when the bot sees someone do an action."""
        msg = msg.replace("./", " /")
        msg = msg.replace(".!", " !")
        msg = msg.replace(".$", " $")
        msg = msg.replace(".+", " +")
        user = user.split('!', 1)[0]
        msg = "".join([char for char in msg if ord(char) < 128 and char != "" or "0"])
        self.factory.queue.put((self, TASK_ACTION, (127, COLOUR_PURPLE, user, msg)))
        #self.logger.info("* %s %s" % (user, msg))
        #self.factory.chatlog.write("[%s] * %s %s\n" % (datetime.datetime.utcnow().strftime("%Y/%m/%d %H:%M:%S"), user, msg))
        #self.factory.chatlog.flush()

    def sendMessage(self, username, message):
        username = self.convertStringToIrc(username)
        message = self.convertStringToIrc(message)
        self.msg(self.factory.irc_channel, "%s: %s" % (username, message))

    def sendServerMessage(self, message,admin=False,user="",IRC=False):
        message = self.convertStringToIrc(message)
        if admin:
            self.msg(self.factory.staffchat_channel, "%s" %message)
        else:
            self.msg(self.factory.irc_channel, "%s" % message)

    def sendAction(self, username, message):
        username = self.convertStringToIrc(username)
        message = self.convertStringToIrc(message)
        self.msg(self.factory.irc_channel, "* %s %s" % (username, message))
            
    def convertStringToIrc(self, string):
        string = string.replace("&0", "01")
        string = string.replace("&1", "02")
        string = string.replace("&2", "03")
        string = string.replace("&3", "10")
        string = string.replace("&4", "05")
        string = string.replace("&5", "06")
        string = string.replace("&6", "07")
        string = string.replace("&7", "15")
        string = string.replace("&8", "14")
        string = string.replace("&9", "12")
        string = string.replace("&a", "09")
        string = string.replace("&b", "11")
        string = string.replace("&c", "04")
        string = string.replace("&d", "13")
        string = string.replace("&e", "08")
        string = string.replace("&f", "")
        string = string.replace("./", " /")
        string = string.replace(".!", " !")
        string = string.replace(".@", " @")
        string = string.replace(".#", " #")
        string = string.replace(".$", " $")
        string = string.replace(".+", " +")
        return string

    # irc callbacks

    def irc_NICK(self, prefix, params):
        "Called when an IRC user changes their nickname."
        old_nick = prefix.split('!')[0]
        new_nick = params[0]
        for channelUserData in self.users.itervalues():
            channelUserData.renameUser(old_nick, new_nick)
        msg = "%s%s is now known as %s" % (COLOUR_YELLOW, old_nick, new_nick)
        self.factory.queue.put((self, TASK_IRCMESSAGE, (127, COLOUR_PURPLE, "IRC", msg)))

    def userKicked(self, kickee, channel, kicker, message):
        "Called when I observe someone else being kicked from a channel."
        self.users[channel.lower()].removeUser(kickee)
        msg = "%s%s was kicked from %s by %s" % (COLOUR_YELLOW, kickee, channel, kicker)
        self.factory.queue.put((self, TASK_IRCMESSAGE, (127, COLOUR_PURPLE, "IRC", msg)))
        if not kickee == message:
            msg = "%sReason: %s" % (COLOUR_YELLOW, message)
            self.factory.queue.put((self, TASK_IRCMESSAGE, (127, COLOUR_PURPLE, "IRC", msg)))

    def userLeft(self, user, channel):
        "Called when I see another user leaving a channel."
        self.users[channel.lower()].removeUser(user)
        msg = "%s%s has left %s" % (COLOUR_YELLOW, user.split("!")[0], channel)
        self.factory.queue.put((self, TASK_IRCMESSAGE, (127, COLOUR_PURPLE, "IRC", msg)))

    def userJoined(self, user, channel):
        "Called when I see another user joining a channel."
        self.users[channel.lower()].all.add(user)
        msg = "%s%s has joined %s" % (COLOUR_YELLOW, user.split("!")[0], channel)
        self.factory.queue.put((self, TASK_IRCMESSAGE, (127, COLOUR_PURPLE, "IRC", msg)))

    def modeChanged(self, user, channel, set, modes, args):
        "Called when someone changes a mode."
        setUser = user.split("!")[0]
        arguments = []
        for element in args:
            if element:
                arguments.append(element.split("!")[0])
        if set and (modes.startswith("o") or modes.startswith("a") or modes.startswith("h") or modes.startswith("q")):
            if len(arguments) < 2:
                msg = "%s%s was opped on %s by %s" % (COLOUR_YELLOW, arguments[0], channel, setUser)
            else:
                msg = "%sUsers opped on %s by %s: %s (%s)" % (COLOUR_YELLOW, channel, setUser, ", ".join(arguments), len(arguments))
            self.factory.queue.put((self, TASK_IRCMESSAGE, (127, COLOUR_PURPLE, "IRC", msg)))
            for name in args:
                self.users[channel.lower()].ops.add(name)
        elif not set and (modes.startswith("o") or modes.startswith("a") or modes.startswith("h") or modes.startswith("q")):
            done = []
            for name in args:
                done.append(name.split("!")[0])
            if len(arguments) < 2:
                msg = "%s%s was deopped on %s by %s" % (COLOUR_YELLOW, arguments[0], channel, setUser)
            else:
                msg = "%sUsers deopped on %s by %s: %s (%s)" % (COLOUR_YELLOW, channel, setUser, ", ".join(arguments), len(arguments))
            self.factory.queue.put((self, TASK_IRCMESSAGE, (127, COLOUR_PURPLE, "IRC", msg)))
            for name in args:
                self.users[channel.lower()].ops.discard(name)
        elif set and modes.startswith("v"):
            if len(arguments) < 2:
                msg = "%s%s was voiced on %s by %s" % (COLOUR_YELLOW, arguments[0], channel, setUser)
            else:
                msg = "%sUsers voiced on %s by %s: %s (%s)" % (COLOUR_YELLOW, channel, setUser, ", ".join(arguments), len(arguments))
            self.factory.queue.put((self, TASK_IRCMESSAGE, (127, COLOUR_PURPLE, "IRC", msg)))
            for name in args:
                self.users[channel.lower()].voice.add(name)
        elif not set and modes.startswith("v"):
            done = []
            for name in args:
                done.append(name.split("!")[0])
            if len(arguments) < 2:
                msg = "%s%s was devoiced on %s by %s" % (COLOUR_YELLOW, arguments[0], channel, setUser)
            else:
                msg = "%sUsers devoiced on %s by %s: %s (%s)" % (COLOUR_YELLOW, channel, setUser, ", ".join(arguments), len(arguments))
            self.factory.queue.put((self, TASK_IRCMESSAGE, (127, COLOUR_PURPLE, "IRC", msg)))
            for name in args:
                self.users[channel.lower()].voice.discard(name)
        elif set and modes.startswith("b"):
            msg = "%sBan set in %s by %s" % (COLOUR_YELLOW, channel, setUser)
            self.factory.queue.put((self, TASK_IRCMESSAGE, (127, COLOUR_PURPLE, "IRC", msg)))
            msg = "%s(%s)" % (COLOUR_YELLOW, " ".join(args))
            self.factory.queue.put((self, TASK_IRCMESSAGE, (127, COLOUR_PURPLE, "IRC", msg)))
        elif not set and modes.startswith("b"):
            msg = "%sBan lifted in %s by %s" % (COLOUR_YELLOW, channel, setUser)
            self.factory.queue.put((self, TASK_IRCMESSAGE, (127, COLOUR_PURPLE, "IRC", msg)))
            msg = "%s(%s)" % (COLOUR_YELLOW, " ".join(args))
            self.factory.queue.put((self, TASK_IRCMESSAGE, (127, COLOUR_PURPLE, "IRC", msg)))
    
    def irc_QUIT(self, user, params):
        userhost = user
        user = user.split('!')[0]
        quitMessage = params[0]
        for channelUserData in self.users.itervalues():
            channelUserData.removeUser(user)
        msg = "%s%s has quit IRC." % (COLOUR_YELLOW, user)
        self.factory.queue.put((self, TASK_IRCMESSAGE, (127, COLOUR_PURPLE, "IRC", msg)))

        msg = msg.replace("0", "&f")
        msg = msg.replace("00", "&f")
        msg = msg.replace("1", "&0")
        msg = msg.replace("01", "&0")
        msg = msg.replace("2", "&1")
        msg = msg.replace("02", "&1")
        msg = msg.replace("3", "&2")
        msg = msg.replace("03", "&2")
        msg = msg.replace("4", "&c")
        msg = msg.replace("04", "&c")
        msg = msg.replace("5", "&4")
        msg = msg.replace("05", "&4")
        msg = msg.replace("6", "&5")
        msg = msg.replace("06", "&5")
        msg = msg.replace("7", "&6")
        msg = msg.replace("07", "&6")
        msg = msg.replace("8", "&e")
        msg = msg.replace("08", "&e")
        msg = msg.replace("9", "&a")
        msg = msg.replace("09", "&a")
        msg = msg.replace("10", "&3")
        msg = msg.replace("11", "&b")
        msg = msg.replace("12", "&9")
        msg = msg.replace("13", "&d")
        msg = msg.replace("14", "&8")
        msg = msg.replace("15", "&7")
        goodchars = ["a", "b", "c", "d", "e", "f", "g", "h", "i", "j", "k", "l", "m", "n", "o", "p", "q", "r", "s", "t", "u", "v", "w", "x", "y", "z", " ", "0", "1", "2", "3", "4", "5", "6", "7", "8", "9", " ", "!", "@", "#", "$", "%", "*", "(", ")", "-", "_", "+", "=", "{", "[", "}", "]", ":", ";", "\"", "\'", "<", ",", ">", ".", "?", "/", "\\", "|", "^", "~"]
        for character in msg:
            if not character.lower() in goodchars:
                msg = msg.replace(character, "*")
        msg = msg.replace("%0", "&0")
        msg = msg.replace("%1", "&1")
        msg = msg.replace("%2", "&2")
        msg = msg.replace("%3", "&3")
        msg = msg.replace("%4", "&4")
        msg = msg.replace("%5", "&5")
        msg = msg.replace("%6", "&6")
        msg = msg.replace("%7", "&7")
        msg = msg.replace("%8", "&8")
        msg = msg.replace("%9", "&9")
        msg = msg.replace("%a", "&a")
        msg = msg.replace("%b", "&b")
        msg = msg.replace("%c", "&c")
        msg = msg.replace("%d", "&d")
        msg = msg.replace("%e", "&e")
        msg = msg.replace("%f", "&f")
        msg = msg.replace("./", " /")
        msg = msg.replace(".!", " !")
        msg = msg.replace(".$", " $")
        msg = msg.replace(".+", " +")
        if msg[len(msg)-2] == "&":
            return
        if len(msg) > 51:
            moddedmsg = msg[:51].replace(" ", "")
            if moddedmsg[len(moddedmsg)-2] == "&":
                msg = msg.replace("&", "*")
        msg = "%s(%s%s)" % (COLOUR_YELLOW, quitMessage, COLOUR_YELLOW)
        self.factory.queue.put((self, TASK_IRCMESSAGE, (127, COLOUR_PURPLE, "IRC", msg)))
        
    def userHasVoicePlus(self, username):
        for channelUserData in self.users.itervalues():
            if username in channelUserData.voice or username in channelUserData.ops:
                return True
        return False
    
    def userHasOps(self, username):
        for channelUserData in self.users.itervalues():
            if username in channelUserData.ops:
                return True
        return False
        
    def getVoiceList(self):
        allVoiceSet = set()
        for channelUserData in self.users.itervalues():
            allVoiceSet.update(channelUserData.voice)
        return list(allVoiceSet)
        
    def getOpList(self):
        allOpSet = set()
        for channelUserData in self.users.itervalues():
            allOpSet.update(channelUserData.ops)
        return list(allOpSet)

class ChatBotFactory(protocol.ClientFactory):
    # the class of the protocol to build when new connection is made
    protocol = ChatBot
    rebootFlag = 0

    def __init__(self, main_factory):
        self.main_factory = main_factory
        self.instance = None
        self.rebootFlag = 1
    
    def quit(self, msg):
        self.rebootFlag = 0
        self.main_factory.logger.info("IRC QUIT :" + msg)
        if self.instance:
            self.instance.sendLine("QUIT :" + msg)

    def clientConnectionLost(self, connector, reason):
        """If we get disconnected, reconnect to server."""
        self.instance = None
        if(self.rebootFlag):
            connector.connect()

    def clientConnectionFailed(self, connector, reason):
        self.main_factory.logger.info("IRC connection failed: %s" % reason)
        if self.instance:
            self.instance.logger.critical("IRC connection failed: %s" % reason)
            self.instance = None
        if not self.main_factory.use_backup_irc:
            self.main_factory.logger.info("Attempting to use the backup IRC server")
            self.main_factory.use_backup_irc = True
            self.main_factory.reloadIrcBot()
        else:
            self.main_factory.logger.info("Failed to connect to all configured IRC servers")
            self.main_factory.use_backup_irc = False

    def sendMessage(self, username, message):
        if self.instance:
            self.instance.sendMessage(username, message)

    def sendAction(self, username, message):
        if self.instance:
            self.instance.sendAction(username, message)

    def sendServerMessage(self, message,admin=False,user="",IRC=False):
        if self.instance:
            self.instance.sendServerMessage(message, admin, user, IRC)
            
    def getIrcUsers(self):
        if self.instance:
            return list(self.instance.users[self.main_factory.irc_channel.lower()].all)
        else:
            return []
            
    def getIrcStaffChatUsers(self):
        if self.instance:
            return list(self.instance.users[self.main_factory.staffchat_channel.lower()].all)
        else:
            return []