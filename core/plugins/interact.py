#    Copyright 2010-2011 to
#    <James Kirslis> james@helplarge.com AKA "iKJames"
#    <Joseph Connor> destroyerx100@gmail.com AKA "destroyerx1"
#    <Nick Tolrud> ntolrud@yahoo.com AKA "ntfwc"
#    <Randy Lyne> qcksilverdragon@gmail.com AKA "goober"
#    <Willem van der Ploeg> willempieeploeg@live.nl AKA "willempiee"
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you
#    may not use this file except in compliance with the License. You may
#    obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS,
#    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
#    implied. See the License for the specific language governing
#    permissions and limitations under the License.

import logging, traceback, random, time, cPickle
from reqs.twisted.internet import reactor
from core.plugins import ProtocolPlugin
from core.decorators import *
from core.constants import *
from core.timer import ResettableTimer
var_version = "0.61"
var_maxcommandsperblock = 100

class CommandPlugin(ProtocolPlugin):
    
    commands = {
        "cmdhelp": "commandCmdHelp",
        "cmdabout": "commandCmdAbout",
        "cmd": "commandCommand",
        "gcmd": "commandGuestCommand",
        "scmd": "commandSensorCommand",
        "gscmd": "commandGuestSensorCommand",
        "cmdend": "commandCommandend",
        "cmddel": "commandCommanddel",
        "cmddelend": "commandCommanddelend",
        "cmdshow": "commandShowcmdblocks",
        "cmdinfo": "commandcmdinfo",
        "cmddelcmd": "commandcmddelcmd",
        "r": "commandRepeat",
        "lastcmd": "commandLastCommand",
    }
    
    hooks = {
        "blockclick": "blockChanged",
        "newworld": "newWorld",
        "poschange": "posChanged",
        "chatmsg": "message"
    }
    
    def gotClient(self):
        self.twocoordcommands = list(["blb", "bhb", "bwb", "bcb", "bchb", "bfb", "mountain", "hill", "dune", "pit", "lake", "hole", "copy", "replace","line"])
        self.onecoordcommands = list(["sphere", "hsphere", "paste", "pasta", "bob", "circle"])
        self.command_remove = False
        self.last_block_position = None
        self.command_cmd = list({})
        self.command_dest = None
        self.placing_cmd = False
        self.cmdinfo = False
        self.runningcmdlist = list({})
        self.runningsensor = False
        self.listeningforpay = False
        self.inputvar = None
        self.inputnum = None
        self.inputblock = None
        self.inputyn = None
        self.customvars = dict({})
        self.cmdinfolines = None
        self.infoindex = None
        self.lastcommand = None
        self.savedcommands = list({})

    def loadBank(self):
        file = open('config/data/balances.dat', 'r')
        bank_dic = cPickle.load(file)
        file.close()
        return bank_dic

    def message(self, message):
        if message.startswith("/") and not (message.split()[0].lower() == "/lastcmd" or message.split()[0].lower() == "/r"):
            self.lastcommand = message
        if self.cmdinfolines is not None:
            if message.lower() == "next":
                self.infoindex+=10
                index = int(self.infoindex)
                cmdlist = self.cmdinfolines[index:index+10]
                if len(cmdlist) < 10:
                    if len(cmdlist) > 0:
                        self.client.sendServerMessage("Page %s of %s:" %(int((index+11)/10), int((len(self.cmdinfolines)/10)+1)))
                        for x in cmdlist:
                            self.client.sendServerMessage(x)
                    self.client.sendServerMessage("Reached the end.")
                    self.infoindex = None
                    self.cmdinfolines = None
                    return True
                self.client.sendServerMessage("Page %s of %s:" %(int((index+11)/10), int((len(self.cmdinfolines)/10)+1)))
                for x in cmdlist:
                    self.client.sendServerMessage(x)
                return True
            elif message.lower() == "back":
                self.infoindex-=10
                try:
                    cmdlist = self.cmdinfolines[self.infoindex:self.infoindex+10]
                except:
                    self.infoindex+=10
                    self.client.sendServerMessage("Reached the beginning.")
                    return
                self.client.sendServerMessage("Page %s of %s:" %(int((self.infoindex+1)/10), int(len(self.cmdinfolist)/10)))
                for x in cmdlist:
                    self.client.sendServerMessage(x)
                return True
            elif message.lower() == "cancel":
                self.infoindex = None
                self.cmdinfolines = None
                return True
            else:
                self.client.sendServerMessage("Please use next, back, or cancel.")
                return True
        if self.listeningforpay:
            if message.lower() == "y" or message.lower() == "yes":
                self.listeningforpay = False
                self.client.sendServerMessage("Payment confirmed!")
                try:
                    x = self.runningcmdlist[0]
                except IndexError:
                    return
                runcmd = True
                thiscmd = x
                thiscmd = thiscmd.replace(" /", "/") # sometimes the meta file stores it with a leading space
                if thiscmd.startswith("/gcmd"):
                    guest = True
                    runcmd = not self.runningsensor
                elif thiscmd.startswith("/gscmd"):
                    guest = True
                    runcmd = self.runningsensor
                elif thiscmd.startswith("/scmd"):
                    guest = False
                    runcmd = self.runningsensor
                else:
                    guest = False
                    runcmd = not self.runningsensor
                thiscmd = thiscmd.replace("/gcmd", "")
                thiscmd = thiscmd.replace("/cmd", "")
                thiscmd = thiscmd.replace("/gscmd", "")
                thiscmd = thiscmd.replace("/scmd", "")
                thiscmd = thiscmd.replace("$name", self.client.username)
                thiscmd = thiscmd.replace("$date", time.strftime("%m/%d/%Y",time.localtime(time.time())))
                thiscmd = thiscmd.replace("$time", time.strftime("%H:%M:%S",time.localtime(time.time())))
                parts = thiscmd.split()
                command = str(parts[0])
                self.runningcmdlist.remove(x)
                reactor.callLater(0.01, self.runcommands)
                if not command.lower() in self.client.commands:
                    if runcmd:
                        self.client.sendServerMessage("Unknown command '%s'" % command)
                    runcmd = False
                try:
                    func = self.client.commands[command.lower()]
                except KeyError:
                    if runcmd:
                        self.client.sendServerMessage("Unknown command '%s'" % command)
                    runcmd = False
                try:
                    if runcmd:
                        func(parts, False, guest)
                except UnboundLocalError:
                    self.client.sendSplitServerMessage(traceback.format_exc().replace("Traceback (most recent call last):", ""))
                    self.client.sendSplitServerMessage("Internal Server Error - Traceback (Please report this to the Server Staff or the iCraft Team, see /about for contact info)")
                    self.client.logger.error(traceback.format_exc())
            elif message.lower() == "n" or message.lower() == "no":
                self.listeningforpay = False
                self.runningcmdlist = list({})
                self.runningsensor = False
                self.listeningforpay = False
                self.client.sendServerMessage("Payment declined.")
            else:
                self.client.sendServerMessage("Please use 'y' or 'n' to confirm.")
            return True
        if self.inputvar:
            self.customvars[self.inputvar] = message
            self.inputvar = None
            reactor.callLater(0.01, self.runcommands)
            return True
        if self.inputnum:
            try:
                int(message)
            except ValueError:
                self.client.sendServerMessage("Please enter an valid integer.")
                return True
            self.customvars[self.inputnum] = message
            self.inputnum = None
            reactor.callLater(0.01, self.runcommands)
            return True
        if self.inputblock:
            try:
                block = ord(self.client.GetBlockValue(message))
            except TypeError:
                # it was invalid
                return True
            if 49<block<0:
                self.client.sendServerMessage("Invalid block number.")
                return True
            self.customvars[self.inputblock] = message
            self.inputblock = None
            reactor.callLater(0.01, self.runcommands)
            return True
        if self.inputyn:
            if message=="y":
                self.customvars[self.inputyn] = message
                self.inputyn = None
                reactor.callLater(0.01, self.runcommands)
                return True
            elif message=="n":
                self.customvars[self.inputyn] = message
                self.inputyn = None
                reactor.callLater(0.01, self.runcommands)
                return True
            else:
                self.client.sendServerMessage("Please answer yes or no.")
                return True

    def blockChanged(self, x, y, z, block, fromloc):
        "Hook trigger for block changes."
        # avoid infinite loops by making blocks unaffected by commands
        if fromloc != "user":
            return False
        if self.client.world.has_command(x, y, z):
            if self.cmdinfo:
                cmdlist = self.client.world.get_command(x, y, z)
                if len(cmdlist)<11:
                    self.client.sendServerMessage("Page 1 of 1:")
                    for x in cmdlist:
                        self.client.sendServerMessage(x)
                else:
                    self.client.sendServerMessage("Page 1 of %s:" %int((len(cmdlist)/10)+1))
                    for x in cmdlist[:9]:
                        self.client.sendServerMessage(x)
                    self.infoindex = 0
                    self.cmdinfolines = cmdlist
                return False
            if self.command_remove is True:
                self.client.world.delete_command(x, y, z)
                self.client.sendServerMessage("You deleted a command block.")
            else:
                if self.listeningforpay:
                    self.client.sendServerMessage("Please confirm or cancel payment before using a cmdblock.")
                    return False

                if self.inputvar is not None or self.inputnum is not None or self.inputblock is not None or self.inputyn is not None:
                    self.client.sendServerMessage("Please give input before using a cmdblock")
                    return False
                if self.cmdinfolines is not None:
                    self.client.sendServerMessage("Please complete the cmdinfo before using a cmdblock.")
                    return False
                self.runningcmdlist = list(self.client.world.get_command(x, y, z))
                self.runningsensor = False
                reactor.callLater(0.01, self.runcommands)
                return False
        if self.command_cmd:
            if self.placing_cmd:
                self.client.sendServerMessage("You placed a command block. Type /cmdend to stop.")
                self.client.world.add_command(x, y, z, self.command_cmd)

    def newWorld(self, world):
        "Hook to reset Command abilities in new worlds if not op."
        if not self.client.isBuilderPlus():
            self.command_cmd = None
            self.command_remove = False
            
    def posChanged(self, x, y, z, h, p):
        "Hook trigger for when the user moves"
        rx = x >> 5
        ry = y >> 5
        rz = z >> 5
        try:
            if self.client.world.has_command(rx, ry, rz) and (rx, ry, rz) != self.last_block_position:
                if self.listeningforpay:
                    self.client.sendServerMessage("Please confirm or cancel payment before using a cmdblock.")
                    return False
                if self.inputvar is not None or self.inputnum is not None or self.inputblock is not None or self.inputyn is not None:
                    self.client.sendServerMessage("Please give input before using a cmdblock")
                    return False
                self.runningcmdlist = list(self.client.world.get_command(rx, ry, rz))
                self.runningsensor = True
                reactor.callLater(0.01, self.runcommands)
        except AssertionError:
            pass
        self.last_block_position = (rx, ry, rz)

    @info_list
    def commandCmdHelp(self, parts, fromloc, overriderank):
        "/cmdhelp - Guest\nGets the help document for Interact."
        self.client.sendSplitServerMessage("See the latest document for Interact scripting at: http://bit.ly/gn8U63")
        self.client.sendServerMessage("Other Commands:")
        self.client.sendServerMessage("/cmdabout - Checks about Interact.")

    @info_list
    def commandCmdAbout(self, parts, fromloc, overriderank):
        "/cmdabout - Guest\nGives information about Interact."
        self.client.sendServerMessage("Interact Version %s" % (var_version))
        self.client.sendServerMessage("Created by destroyerx1")
        self.client.sendServerMessage("Developed by iKJames")

    @info_list
    def commandRepeat(self, parts, fromloc, rankoverride):
        "/r - Guest\nRepeats the last command that you used."
        message = self.lastcommand
        try:
            parts = [x.strip() for x in message.split() if x.strip()]
        except:
            self.client.sendServerMessage("You haven't used a command yet.")
            return
        command = parts[0].strip("/")
        self.client.logger.info("%s just used: %s" % (self.client.username, " ".join(parts)))
        # See if we can handle it internally
        try:
            func = getattr(self.client, "command%s" % command.title())
        except AttributeError:
            # Can we find it from a plugin?
            try:
                func = self.client.commands[command.lower()]
            except KeyError:
                self.client.sendServerMessage("Unknown command '%s'" % command)
                return
        if (self.client.isSpectator() and (getattr(func, "admin_only", False) or getattr(func, "mod_only", False) or getattr(func, "op_only", False) or getattr(func, "worldowner_only", False) or getattr(func, "member_only", False) or getattr(func, "builder_only", False))):
            if fromloc == "user":
                self.client.sendServerMessage("'%s' is not available to specs." % command)
                return
        if getattr(func, "director_only", False) and not self.client.isDirectorPlus():
            if fromloc == "user":
                self.client.sendServerMessage("'%s' is a Director-only command!" % command)
                return
        if getattr(func, "coder_only", False) and not self.client.isCoderPlus():
            if fromloc == "user":
                self.client.sendServerMessage("'%s' is an Admin-only command!" % command)
                return
        if getattr(func, "admin_only", False) and not self.client.isAdminPlus():
            if fromloc == "user":
                self.client.sendServerMessage("'%s' is an Admin-only command!" % command)
                return
        if getattr(func, "mod_only", False) and not self.client.isModPlus():
            if fromloc == "user":
                self.client.sendServerMessage("'%s' is a Mod-only command!" % command)
                return
        if getattr(func, "worldowner_only", False) and not self.client.isWorldOwnerPlus():
            if fromloc == "user":
                self.client.sendServerMessage("'%s' is an WorldOwner-only command!" % command)
                return
        if getattr(func, "op_only", False) and not self.client.isOpPlus():
            if fromloc == "user":
                self.client.sendServerMessage("'%s' is an Op-only command!" % command)
                return
        if getattr(func, "builder_only", False) and not self.client.isBuilderPlus():
            if fromloc == "user":
                self.client.sendServerMessage("'%s' is a Builder-only command!" % command)
                return
        if getattr(func, "member_only", False) and not self.client.isMemberPlus():
            if fromloc == "user":
                self.client.sendServerMessage("'%s' is a Member-only command!" % command)
                return
        try:
            func(parts, "user", False) # fromloc is user, overriderank is false
        except Exception, e:
            self.client.sendSplitServerMessage(traceback.format_exc().replace("Traceback (most recent call last):", ""))
            self.client.sendSplitServerMessage("Internal Server Error - Traceback (Please report this to the Server Staff or the iCraft Team, see /about for contact info)")
            self.client.logger.error(traceback.format_exc())
            
            
    @mod_only
    @username_command
    def commandLastCommand(self, user, fromloc, overriderank, params=[]):
        "/lastcmd - Mod\nShows the last command used by the given user."
        if user.username == self.client.username:
            self.client.sendServerMessage("You last used: %s" % self.lastcommand)
        else:
            for plugin in user.plugins:
                if isinstance(plugin, CommandPlugin):
                    self.client.sendServerMessage("%s last used: %s" % (user.username, plugin.lastcommand))
                    return


    @builder_only
    def commandCommand(self, parts, fromloc, permissionoverride):
        "/cmd command [arguments] - Builder\nStarts creating a command block, or adds a command to the command\nblock. The command can be any server command. After you have\nentered all commands, type /cmd again to begin placing. Once\nplaced, the blocks will run the command when clicked as if the\none clicking had typed the commands."
        if len(parts) < 2:
            if self.command_cmd == list({}):
                self.client.sendServerMessage("Please enter a command.")
            else:
                self.placing_cmd = True
                self.client.sendServerMessage("You are now placing command blocks.")
        else:
            if parts[0] != "//cmd":
                if parts[1] in self.twocoordcommands:
                    if len(parts) <  8:
                        if len(self.client.last_block_changes) > 1:
                            x, y, z = self.client.last_block_changes[0]
                            x2, y2, z2 = self.client.last_block_changes[1]
                            parts.append(x)
                            parts.append(y)
                            parts.append(z)
                            parts.append(x2)
                            parts.append(y2)
                            parts.append(z2)
                if parts[1] in self.onecoordcommands:
                    if len(parts) < 5:
                        if len(self.client.last_block_changes) > 1:
                            x, y, z = self.client.last_block_changes[0]
                            parts.append(x)
                            parts.append(y)
                            parts.append(z)
            parts[0] = "/cmd"
            commandtext = ""
            for x in parts:
                   commandtext = commandtext + " " + str(x)
            if not self.command_cmd is None:
                if len(self.command_cmd) >= var_maxcommandsperblock:
                        self.client.sendServerMessage("You can only use %s commands per block!" % var_maxcommandsperblock)
                else:
                    var_string = ""
                    var_cmdparts = parts[1:]
                    for index in range(len(var_cmdparts)):
                        if index == 0:
                            var_string = var_string + str(var_cmdparts[0])
                        else:
                            var_string = var_string + ' ' + str(var_cmdparts[index])
                    self.command_cmd.append(commandtext)
                    if len(self.command_cmd) > 1:     
                        self.client.sendServerMessage("Command %s added." % var_string)
                    else:
                        self.client.sendServerMessage("You are now creating a command block.")
                        self.client.sendServerMessage("Use /cmd command again to add a command")
                        self.client.sendSplitServerMessage("Use //cmd command to add a command without adding any coordinates (for things like blb, sphere, etc.)")
                        self.client.sendServerMessage("Type /cmd with no args to start placing the block.")
                        self.client.sendServerMessage("Command %s added." % var_string)

    @mod_only                    
    def commandGuestCommand(self, parts, fromloc, permissionoverride):
        "/gcmd command [arguments] - Mod\nMakes the next block you place a guest command block."
        if len(parts) < 2:
            if self.command_cmd == list({}):
                self.client.sendServerMessage("Please enter a command.")
            else:
                self.client.sendServerMessage("You are now placing guest command blocks.")
                self.placing_cmd = True
        else:
            if parts[0] != "//gcmd":
                if parts[1] in self.twocoordcommands:
                    if len(parts) <  8:
                        if len(self.client.last_block_changes) > 1:
                            x, y, z = self.client.last_block_changes[0]
                            x2, y2, z2 = self.client.last_block_changes[1]
                            parts.append(x)
                            parts.append(y)
                            parts.append(z)
                            parts.append(x2)
                            parts.append(y2)
                            parts.append(z2)
                            
                if parts[1] in self.onecoordcommands:
                    if len(parts) < 5:
                        if len(self.client.last_block_changes) > 1:
                            x, y, z = self.client.last_block_changes[0]
                            parts.append(x)
                            parts.append(y)
                            parts.append(z)
            parts[0] = "/gcmd"
            commandtext = ""
            command = str(parts[1])
            cmdspecials = ["wait", "if", "exit", "getinput", "getnum", "getblock", "getyn", "self"] # not actual commands but can be used in cmdblocks
            if not command in cmdspecials:
                if command.lower() in self.client.commands:
                    func = self.client.commands[command.lower()]
                else:
                    self.client.sendServerMessage("Unknown command '%s'" % command)
                    return
                if (self.client.isSpectator() and (getattr(func, "admin_only", False) or getattr(func, "mod_only", False) or getattr(func, "op_only", False) or getattr(func, "member_only", False) or getattr(func, "worldowner_only", False) or getattr(func, "builder_only", False))):
                    return
                if getattr(func, "director_only", False):# and not self.client.isDirectorPlus():
                    return
                if getattr(func, "coder_only", False):# and not self.client.isCoderPlus():
                    return
                if getattr(func, "admin_only", False):# and not self.client.isAdminPlus():
                    return
                if getattr(func, "mod_only", False):# and not self.client.isModPlus():
                    return
                if getattr(func, "worldowner_only", False) and not self.client.isWorldOwnerPlus():
                    return
                if getattr(func, "op_only", False) and not self.client.isOpPlus():
                    return
                if getattr(func, "builder_only", False) and not self.client.isBuilderPlus():
                    return
                if getattr(func, "member_only", False) and not self.client.isMemberPlus():
                    return
            for x in parts:
                   commandtext = commandtext + " " + str(x)
            if not self.command_cmd is None:
                if len(self.command_cmd) >= var_maxcommandsperblock:
                        self.client.sendServerMessage("You can only use %s commands per block!" % var_maxcommandsperblock)
                else:
                    var_string = ""
                    var_cmdparts = parts[1:]
                    for index in range(len(var_cmdparts)):
                        if index == 0:
                            var_string = var_string + str(var_cmdparts[0])
                        else:
                            var_string = var_string + ' ' + str(var_cmdparts[index])
                    self.command_cmd.append(commandtext)
                    if len(self.command_cmd) > 1:     
                        self.client.sendServerMessage("Command %s added." % var_string)
                    else:
                        self.client.sendServerMessage("You are now creating a guest command block.")
                        self.client.sendServerMessage("WARNING: Commands on this block can be run by ANYONE")
                        self.client.sendServerMessage("Use /gcmd command again to add a command")
                        self.client.sendSplitServerMessage("Use //gcmd command to add a command without adding any coordinates (for things like blb, sphere, etc.)")
                        self.client.sendServerMessage("Type /gcmd with no args to start placing the block.")
                        self.client.sendServerMessage("Command %s added." % var_string)
                        
    @builder_only
    def commandSensorCommand(self, parts, fromloc, permissionoverride):
        "/scmd command [arguments] - Builder\nStarts creating a command block, or adds a command to the command\nblock. The command can be any server command. After you have\nentered all commands, type /cmd again to begin placing. Once\nplaced, the blocks will run the command when clicked as if the\none clicking had typed the commands."
        if len(parts) < 2:
            if self.command_cmd == list({}):
                self.client.sendServerMessage("Please enter a command.")
            else:
                self.placing_cmd = True
                self.client.sendServerMessage("You are now placing sensor command blocks.")
        else:
            if parts[0] != "//scmd":
                if parts[1] in self.twocoordcommands:
                    if len(parts) <  8:
                        if len(self.client.last_block_changes) > 1:
                            x, y, z = self.client.last_block_changes[0]
                            x2, y2, z2 = self.client.last_block_changes[1]
                            parts.append(x)
                            parts.append(y)
                            parts.append(z)
                            parts.append(x2)
                            parts.append(y2)
                            parts.append(z2)
                if parts[1] in self.onecoordcommands:
                    if len(parts) < 5:
                        if len(self.client.last_block_changes) > 1:
                            x, y, z = self.client.last_block_changes[0]
                            parts.append(x)
                            parts.append(y)
                            parts.append(z)
            parts[0] = "/scmd"
            commandtext = ""
            for x in parts:
                   commandtext = commandtext + " " + str(x)
            if not self.command_cmd is None:
                if len(self.command_cmd) >= var_maxcommandsperblock:
                        self.client.sendServerMessage("You can only use %s commands per block!" % var_maxcommandsperblock)
                else:
                    var_string = ""
                    var_cmdparts = parts[1:]
                    for index in range(len(var_cmdparts)):
                        if index == 0:
                            var_string = var_string + str(var_cmdparts[0])
                        else:
                            var_string = var_string + ' ' + str(var_cmdparts[index])
                    self.command_cmd.append(commandtext)
                    if len(self.command_cmd) > 1:     
                        self.client.sendServerMessage("Command %s added." % var_string)
                    else:
                        self.client.sendServerMessage("You are now creating a sensor command block.")
                        self.client.sendServerMessage("Use /scmd command again to add a command.")
                        self.client.sendSplitServerMessage("Use //scmd command to add a command without adding any coordinates (for things like blb, sphere, etc.)")
                        self.client.sendServerMessage("Type /scmd with no args to start placing the block.")
                        self.client.sendServerMessage("Command %s added." % var_string)
                        
    @mod_only
    def commandGuestSensorCommand(self, parts, fromloc, permissionoverride):
        "/gscmd command [arguments] - Mod\nMakes the next block you place a guest sensor command block."
        if len(parts) < 2:
            if self.command_cmd == list({}):
                self.client.sendServerMessage("Please enter a command.")
            else:
                self.client.sendServerMessage("You are now placing guest sensor command blocks.")
                self.placing_cmd = True
        else:
            if parts[0] != "//gscmd":
                if parts[1] in self.twocoordcommands:
                    if len(parts) <  8:
                        if len(self.client.last_block_changes) > 1:
                            x, y, z = self.client.last_block_changes[0]
                            x2, y2, z2 = self.client.last_block_changes[1]
                            parts.append(x)
                            parts.append(y)
                            parts.append(z)
                            parts.append(x2)
                            parts.append(y2)
                            parts.append(z2)
                if parts[1] in self.onecoordcommands:
                    if len(parts) < 5:
                        if len(self.client.last_block_changes) > 1:
                            x, y, z = self.client.last_block_changes[0]
                            parts.append(x)
                            parts.append(y)
                            parts.append(z)
            parts[0] = "/gscmd"
            commandtext = ""
            command = str(parts[1])
            cmdspecials = ["wait", "if", "exit", "getinput", "getnum", "getblock", "getyn", "self"]  # not actual commands but can be used in cmdblocks
            if not command in cmdspecials:
                if command.lower() in self.client.commands:
                    func = self.client.commands[command.lower()]
                else:
                    self.client.sendServerMessage("Unknown command '%s'" % command)
                    return
                if (self.client.isSpectator() and (getattr(func, "admin_only", False) or getattr(func, "mod_only", False) or getattr(func, "op_only", False) or getattr(func, "member_only", False) or getattr(func, "worldowner_only", False) or getattr(func, "builder_only", False))):
                    self.client.sendServerMessage("'%s' is not available to specs." % command)
                    return
                if getattr(func, "director_only", False):# and not self.client.isDirectorPlus():
                    self.client.sendServerMessage("'%s' is a Director-only command!" % command)
                    return
                if getattr(func, "coder_only", False):# and not self.client.isCoderPlus():
                    self.client.sendServerMessage("'%s' is an Admin-only command!" % command)
                    return
                if getattr(func, "admin_only", False):# and not self.client.isAdminPlus():
                    self.client.sendServerMessage("'%s' is an Admin-only command!" % command)
                    return
                if getattr(func, "mod_only", False):# and not self.client.isModPlus():
                    self.client.sendServerMessage("'%s' is a Mod-only command!" % command)
                    return
                if getattr(func, "worldowner_only", False) and not self.client.isWorldOwnerPlus():
                    self.client.sendServerMessage("'%s' is an WorldOwner-only command!" % command)
                    return
                if getattr(func, "op_only", False) and not self.client.isOpPlus():
                    self.client.sendServerMessage("'%s' is an Op-only command!" % command)
                    return
                if getattr(func, "builder_only", False) and not self.client.isBuilderPlus():
                    self.client.sendServerMessage("'%s' is a Builder-only command!" % command)
                    return
                if getattr(func, "member_only", False) and not self.client.isMemberPlus():
                    self.client.sendServerMessage("'%s' is a Member-only command!" % command)
                    return
            for x in parts:
                   commandtext = commandtext + " " + str(x)
            if not self.command_cmd is None:
                if len(self.command_cmd) >= var_maxcommandsperblock:
                        self.client.sendServerMessage("You can only use %s commands per block!" % var_maxcommandsperblock)
                else:
                    var_string = ""
                    var_cmdparts = parts[1:]
                    for index in range(len(var_cmdparts)):
                        if index == 0:
                            var_string = var_string + str(var_cmdparts[0])
                        else:
                            var_string = var_string + ' ' + str(var_cmdparts[index])
                    self.command_cmd.append(commandtext)
                    if len(self.command_cmd) > 1:     
                        self.client.sendServerMessage("Command %s added." % var_string)
                    else:
                        self.client.sendServerMessage("You are now creating a guest sensor command block.")
                        self.client.sendServerMessage("WARNING: Commands on this block can be run by ANYONE.")
                        self.client.sendServerMessage("Use /gscmd command again to add a command.")
                        self.client.sendSplitServerMessage("Use //gscmd command to add a command without adding any coordinates (for things like blb, sphere, etc.)")
                        self.client.sendServerMessage("Type /gscmd with no args to start placing the block.")
                        self.client.sendServerMessage("Command %s added." % var_string)

    @builder_only
    def commandCommandend(self, parts, fromloc, permissionoverride):
        "/cmdend [save]- Builder\nStops placing command blocks (type save to save your commands)."
        if len(parts) == 2:
            if parts[1] == 'save':
                self.client.sendServerMessage("Current command block and its commands maintained")
            else:
                self.command_cmd = list({})
        else:
            self.command_cmd = list({})
        self.command_remove = False
        self.placing_cmd = False
        self.client.sendServerMessage("You are no longer placing command blocks.")
        self.client.sendSplitServerMessage("Note: you can type '/cmdend save' to keep the block you are making and it's commands.")

    @builder_only
    def commandCommanddel(self, parts, fromloc, permissionoverride):
        "/cmddel - Builder\nEnables command deleting mode"
        self.client.sendServerMessage("You are now able to delete command blocks. /cmddelend to stop")
        self.command_remove = True

    @builder_only
    def commandcmddelcmd(self, parts, fromloc, permissionoverride):
        "/cmddel - Builder\nDeletes the previous command for the block."
        if len(self.command_cmd) > 0:
            del self.command_cmd[len(self.command_cmd)-1]
            self.client.sendServerMessage("Previous command, for the block, deleted")
        else:
            self.client.sendServerMessage("There is no block command to delete")

    @builder_only
    def commandCommanddelend(self, parts, fromloc, permissionoverride):
        "/cmddelend - Builder\nDisables command deleting mode"
        self.client.sendServerMessage("Command deletion mode ended.")
        self.command_remove = False

    @builder_only
    def commandShowcmdblocks(self, parts, fromloc, permissionoverride):
       "/cmdshow - Builder\nShows all command blocks as yellow, only to you."
       for offset in self.client.world.commands.keys():
           x, y, z = self.client.world.get_coords(offset)
           self.client.sendPacked(TYPE_BLOCKSET, x, y, z, BLOCK_YELLOW)
       self.client.sendServerMessage("All commands appearing yellow temporarily.")

    @builder_only
    @on_off_command
    def commandcmdinfo(self, onoff, fromloc, permissionoverride):
       "/cmdinfo - Builder\nTells you the commands in a cmdblock"
       self.cmdinfo = onoff == "on"
       self.client.sendServerMessage("Command block info is now %s." %onoff)

    def runcommands(self):
        try:
            x = self.runningcmdlist[0]
        except IndexError:
            self.customvars = dict({})
            return
        runcmd = True
        thiscmd = str(x)
        thiscmd = thiscmd.replace(" /", "/") # sometimes the meta file stores it with a leading space
        if thiscmd.startswith("/gcmd"):
            guest = True
            runcmd = not self.runningsensor
        elif thiscmd.startswith("/gscmd"):
            guest = True
            runcmd = self.runningsensor
        elif thiscmd.startswith("/scmd"):
            guest = False
            runcmd = self.runningsensor
        else:
            guest = False
            runcmd = not self.runningsensor
        thiscmd = thiscmd.replace("/gcmd", "")
        thiscmd = thiscmd.replace("/cmd", "")
        thiscmd = thiscmd.replace("/gscmd", "")
        thiscmd = thiscmd.replace("/scmd", "")
        thiscmd = thiscmd.replace("$name", self.client.username)
        thiscmd = thiscmd.replace("$cname", self.client.colouredUsername())
        bank = self.loadBank()
        user = self.client.username.lower()
        if user in bank:
            balance = bank[user]
        else:
            balance = 0
        thiscmd = thiscmd.replace("$bank", str(balance))
        thiscmd = thiscmd.replace("$first", str(self.client.username in self.client.factory.lastseen))
        thiscmd = thiscmd.replace("$server", self.client.factory.server_name)
        if self.client.factory.irc_relay:
            thiscmd = thiscmd.replace("$irc", self.client.factory.irc_config.get("irc", "server") + " " + self.client.factory.irc_channel)
            thiscmd = thiscmd.replace("$ircchan", self.client.factory.irc_channel)
            thiscmd = thiscmd.replace("$ircnet", self.client.factory.irc_config.get("irc", "server"))
        else:
            thiscmd = thiscmd.replace("$irc", "N/A")
            thiscmd = thiscmd.replace("$ircchan", "N/A")
            thiscmd = thiscmd.replace("$ircnet", "N/A")
        thiscmd = thiscmd.replace("$owner", self.client.factory.owner)
        thiscmd = thiscmd.replace("$year", time.strftime("%Y",time.localtime(time.time())))
        thiscmd = thiscmd.replace("$month", time.strftime("%m",time.localtime(time.time())))
        thiscmd = thiscmd.replace("$day", time.strftime("%d",time.localtime(time.time())))
        thiscmd = thiscmd.replace("$date", time.strftime("%m/%d/%Y",time.localtime(time.time())))
        thiscmd = thiscmd.replace("$rdate", time.strftime("%d/%m/%Y",time.localtime(time.time())))
        thiscmd = thiscmd.replace("$sdate", time.strftime("%m/%d",time.localtime(time.time())))
        thiscmd = thiscmd.replace("$rsdate", time.strftime("%d/%m",time.localtime(time.time())))
        thiscmd = thiscmd.replace("$time", time.strftime("%H:%M:%S",time.localtime(time.time())))
        thiscmd = thiscmd.replace("$hour", time.strftime("%H",time.localtime(time.time())))
        thiscmd = thiscmd.replace("$min", time.strftime("%M",time.localtime(time.time())))
        thiscmd = thiscmd.replace("$sec", time.strftime("%S",time.localtime(time.time())))
        thiscmd = thiscmd.replace("$stime", time.strftime("%H:%M",time.localtime(time.time())))
        myrank = "guest"
        myranknum = 1
        if self.client.isSpectator():
            myrank = "spec"
            myranknum = 0
        elif self.client.isServerOwner():
            myrank = "owner"
            myranknum = 9
        elif self.client.isDirector() or self.client.isHidden():
            myrank = "director"
            myranknum = 8
        elif self.client.isAdmin() or self.client.isCoder():
            myrank = "admin"
            myranknum = 7
        elif self.client.isMod():
            myrank = "mod"
            myranknum = 6
        elif self.client.isWorldOwner():
            myrank = "worldowner"
            myranknum = 5
        elif self.client.isOp():
            myrank = "op"
            myranknum = 4
        elif self.client.isBuilder():
            myrank = "builder"
            myranknum = 3
        elif self.client.isMember():
            myrank = "member"
            myranknum = 2
        rx = self.client.x >> 5
        ry = self.client.y >> 5
        rz = self.client.z >> 5
        thiscmd = thiscmd.replace("$posx", str(rx))
        thiscmd = thiscmd.replace("$posy", str(ry))
        thiscmd = thiscmd.replace("$posz", str(rz))
        thiscmd = thiscmd.replace("$posa", str(rx)+" "+str(ry)+" "+str(rx))
        thiscmd = thiscmd.replace("$rank", myrank)
        thiscmd = thiscmd.replace("$rnum", str(myranknum))
        for variable in self.customvars.keys():
            thiscmd = thiscmd.replace("$"+variable, str(self.customvars[variable]))
        for num in range(len(thiscmd)):
            if thiscmd[num:(num+4)] == "$rnd":
                try:
                    limits = thiscmd[thiscmd.find("(", num)+1:thiscmd.find(")", num+5)].split(",")
                    thiscmd = thiscmd.replace(thiscmd[num:thiscmd.find(")", num)+1], str(random.randint(int(limits[0]), int(limits[1])))) # holy crap this is complicated
                except:
                    self.client.sendServerMessage("$rnd Syntax Error; Use: $rnd(num1,num2)")
        for num in range(len(thiscmd)):
            if thiscmd[num:(num+4)] == "$mod":
                try:
                    limits = thiscmd[thiscmd.find("(", num)+1:thiscmd.find(")", num+5)].split(",")
                    thiscmd = thiscmd.replace(thiscmd[num:thiscmd.find(")", num)+1], str(int(limits[0])%int(limits[1]))) # holy crap this is complicated
                except:
                    self.client.sendServerMessage("$mod Syntax Error; Use: $mod(num1,num2)")
        for num in range(len(thiscmd)):
            if thiscmd[num:(num+6)] == "$block":
                try:
                    coords = thiscmd[thiscmd.find("(", num)+1:thiscmd.find(")", num+5)].split(",")
                    x = int(coords[0])
                    y = int(coords[1])
                    z = int(coords[2])
                    check_offset = self.client.world.blockstore.get_offset(x, y, z)
                    block = ord(self.client.world.blockstore.raw_blocks[check_offset])
                    thiscmd = thiscmd.replace(thiscmd[num:thiscmd.find(")", num)+1], str(block)) # holy crap this is complicated
                except:
                    self.client.sendServerMessage("$block Syntax Error; Use: $block(x,y,z)")
        for num in range(len(thiscmd)):
            if thiscmd[num:(num+4)] == "$bin":
                try:
                    HexBin ={"0":"0000", "1":"0001", "2":"0010", "3":"0011", "4":"0100", "5":"0101", "6":"0110", "7":"0111", "8":"1000", "9":"1001", "A":"1010", "B":"1011", "C":"1100", "D":"1101", "E":"1110", "F":"1111"}
                    coords = thiscmd[thiscmd.find("(", num)+1:thiscmd.find(")", num+5)]#.split(",")
                    thiscmd = thiscmd.replace(thiscmd[num:thiscmd.find(")", num)+1], str("".join([HexBin[i] for i in '%X'%coords[0]]).lstrip('0'))) # holy crap this is complicated
                except:
                    self.client.sendServerMessage("$bin Syntax Error; Use: $bin(x)")
        for num in range(len(thiscmd)):
            if thiscmd[num:(num+5)] == "$eval" or thiscmd[num:(num+4)] == "$int":
                try:
                    parentheses = 0
                    for num2 in range(num+6, len(thiscmd)-1):
                        if thiscmd[num2] == "(":
                            parentheses = parentheses+1
                        elif thiscmd[num2] == ")":
                            parentheses = parentheses-1
                        if parentheses == 0:
                            # We've reached the end of the expression
                            lastindex = num2
                    expression = str(eval(thiscmd[thiscmd.find("(", num)+1:lastindex+1]))
                    thiscmd = thiscmd.replace(thiscmd[num:lastindex+2], expression) # holy crap this is complicated
                except:
                    self.client.sendServerMessage("$eval Syntax Error; Use: $eval(expression)")
        blocklist = ["air", "rock", "grass", "dirt", "cobblestone", "wood", "plant", "solid", "water", "still water", "lava", "still lava", "sand", "gravel", "gold ore", "iron ore", "coal ore", "trunk", "leaf", "sponge", "glass", "red cloth", "orange cloth", "yellow cloth", "lime green cloth", "green cloth", "turquoise cloth", "cyan cloth", "blue cloth", "dark blue cloth", "violet cloth", "purple cloth", "magenta cloth", "pink cloth", "black cloth", "gray cloth", "white cloth", "flower", "rose", "red mushroom", "brown mushroom", "gold", "iron", "double step", "step", "brick", "TNT", "bookshelf", "mossy cobblestone", "obsidian"]
        for num in range(len(thiscmd)):
            if thiscmd[num:(num+6)] == "$bname":
                try:
                    blocknum = int(thiscmd[thiscmd.find("(", num)+1:thiscmd.find(")", num+5)])
                    thiscmd = thiscmd.replace(thiscmd[num:thiscmd.find(")", num)+1], blocklist[blocknum]) # holy crap this is complicated
                except:
                    self.client.sendServerMessage("$bname Syntax Error; Use: $bname(blockint)")
        if thiscmd.startswith(" if"):
            try:
                condition = thiscmd[4:thiscmd.find(":")]
                if (bool(eval(condition, {}, {}))) == False:
                    runcmd=False
                thiscmd = thiscmd.replace(thiscmd[:thiscmd.find(":")+1], "")
            except:
                self.client.sendServerMessage("IF Syntax Error; Use: if \"a\"==\"b\": command")
        parts = thiscmd.split()
        command = str(parts[0])
        # Require confirmation
        if command == "pay":
            try:
                target = parts[1]
                amount = int(parts[2])
            except:
                self.client.sendServerMessage("Pay syntax error.")
                runcmd = False
            if runcmd:
                bank = self.loadBank()
                user = self.client.username.lower()
            if user in bank:
                if bank[user] > amount:
                    self.listeningforpay = True
                    self.client.sendServerMessage("%s is requesting payment of C%s. Pay? [Y/N]" %(target, amount))
                    return
                else:
                    self.client.sendServerMessage("You don't have enough money to pay!")
                    self.runningcmdlist = list({})
                    self.runningsensor = False
                    return
            else:
                self.client.sendServerMessage("You don't have a bank account!")
                self.runningcmdlist = list({})
                self.runningsensor = False
                return
        # Look for command
        if command == "self" and runcmd:
            msg = ""
            parts.pop(0)
            msg = " ".join(parts)
            self.client._sendMessage(COLOUR_GREEN, msg)
            runcmd = False
        if command == "wait" and runcmd:
            delay = float(0.1)
            try:
                delay = float(parts[1])
            except:
                self.client.sendServerMessage("Wait time must be a number!")
                runcmd = False
            self.runningcmdlist.remove(self.runningcmdlist[0])
            reactor.callLater(delay, self.runcommands)
            return
        if command == "exit" and runcmd:
            self.runningcmdlist = list({})
            return
        if command == "getinput" and runcmd:
            try:
                self.inputvar = parts[1]
            except IndexError:
                self.client.sendServerMessage("You must give a variable name!")
                runcmd = False
            if runcmd:
                if len(parts)>2:
                    self.client.sendServerMessage("[INPUT] "+" ".join(parts[2:]))
                else:
                    self.client.sendServerMessage("This command block is requesting input.")
                self.runningcmdlist.remove(self.runningcmdlist[0])
                return
        if command == "getnum" and runcmd:
            try:
                self.inputnum = parts[1]
            except IndexError:
                self.client.sendServerMessage("You must give a variable name!")
                runcmd = False
            if runcmd:
                if len(parts)>2:
                    self.client.sendServerMessage("[INPUT] "+" ".join(parts[2:]))
                else:
                    self.client.sendServerMessage("This command block is requesting input.")
                self.runningcmdlist.remove(self.runningcmdlist[0])
                return
        if command == "getblock" and runcmd:
            try:
                self.inputblock = parts[1]
            except IndexError:
                self.client.sendServerMessage("You must give a variable name!")
                runcmd = False
            if runcmd:
                if len(parts)>2:
                    self.client.sendServerMessage("[BLOCK INPUT] "+" ".join(parts[2:]))
                else:
                    self.client.sendServerMessage("This command block is requesting block input.")
                self.runningcmdlist.remove(self.runningcmdlist[0])
                return
        if command == "getyesno" and runcmd:
            try:
                self.inputyn = parts[1]
            except IndexError:
                self.client.sendServerMessage("You must give a variable name!")
                runcmd = False
            if runcmd:
                if len(parts)>2:
                    self.client.sendServerMessage("[Y/N] "+" ".join(parts[2:]))
                else:
                    self.client.sendServerMessage("This command block is requesting yes/no input.")
                self.runningcmdlist.remove(self.runningcmdlist[0])
                return
        try:
            if not command.lower() in self.client.commands:
                if runcmd:
                    self.client.sendServerMessage("Unknown command '%s'" % command)
                runcmd = False
            func = self.client.commands[command.lower()]
        except KeyError:
            if runcmd:
                self.client.sendServerMessage("Unknown command '%s'" % command)
                runcmd = False
        if runcmd is True:
            if guest is False:
                if (self.client.isSpectator() and (getattr(func, "admin_only", False) or getattr(func, "mod_only", False) or getattr(func, "op_only", False) or getattr(func, "member_only", False) or getattr(func, "worldowner_only", False) or getattr(func, "builder_only", False))):
                    self.client.sendServerMessage("'%s' is not available to specs." % command)
                    runcmd = False
                if getattr(func, "director_only", False):# and not self.client.isDirectorPlus():
                    self.client.sendServerMessage("'%s' is a Director-only command!" % command)
                    runcmd = False
                if getattr(func, "coder_only", False):# and not self.client.isCoderPlus():
                    self.client.sendServerMessage("'%s' is an Admin-only command!" % command)
                    runcmd = False
                if getattr(func, "admin_only", False):# and not self.client.isAdminPlus():
                    self.client.sendServerMessage("'%s' is an Admin-only command!" % command)
                    runcmd = False
                if getattr(func, "mod_only", False):# and not self.client.isModPlus():
                    self.client.sendServerMessage("'%s' is a Mod-only command!" % command)
                    runcmd = False
                if getattr(func, "worldowner_only", False) and not self.client.isWorldOwnerPlus():
                    self.client.sendServerMessage("'%s' is an WorldOwner-only command!" % command)
                    runcmd = False
                if getattr(func, "op_only", False) and not self.client.isOpPlus():
                    self.client.sendServerMessage("'%s' is an Op-only command!" % command)
                    runcmd = False
                if getattr(func, "builder_only", False) and not self.client.isBuilderPlus():
                    self.client.sendServerMessage("'%s' is a Builder-only command!" % command)
                    runcmd = False
                if getattr(func, "member_only", False) and not self.client.isMemberPlus():
                    self.client.sendServerMessage("'%s' is a Member-only command!" % command)
                    runcmd = False
            else:
                if getattr(func, "director_only", False):# and not self.client.isDirectorPlus():
                    self.client.sendServerMessage("'%s' is a Director-only command!" % command)
                    runcmd = False
                if getattr(func, "coder_only", False):# and not self.client.isCoderPlus():
                    self.client.sendServerMessage("'%s' is an Admin-only command!" % command)
                    runcmd = False
                if getattr(func, "admin_only", False):# and not self.client.isAdminPlus():
                    self.client.sendServerMessage("'%s' is an Admin-only command!" % command)
                    runcmd = False
                if getattr(func, "mod_only", False):# and not self.client.isModPlus():
                    self.client.sendServerMessage("'%s' is a Mod-only command!" % command)
                    runcmd = False
            try:
                try:
                    if runcmd:
                        func(parts, False, guest)
                except UnboundLocalError:
                    self.client.sendSplitServerMessage(traceback.format_exc().replace("Traceback (most recent call last):", ""))
                    self.client.sendSplitServerMessage("Internal Server Error - Traceback (Please report this to the Server Staff or the iCraft Team, see /about for contact info)")
                    self.client.logger.error(traceback.format_exc())
            except Exception, e:
                self.client.sendSplitServerMessage(traceback.format_exc().replace("Traceback (most recent call last):", ""))
                self.client.sendSplitServerMessage("Internal Server Error - Traceback (Please report this to the Server Staff or the iCraft Team, see /about for contact info)")
                self.client.logger.error(traceback.format_exc())
        self.runningcmdlist.remove(self.runningcmdlist[0])
        reactor.callLater(0.1, self.runcommands)
