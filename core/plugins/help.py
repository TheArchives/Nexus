#    iCraft is Copyright 2010-2011 both
#
#    The Archives team:
#                   <Adam Guy> adam@adam-guy.com AKA "Adam01"
#                   <Andrew Godwin> andrew@aeracode.org AKA "Aera"
#                   <Dylan Lukes> lukes.dylan@gmail.com AKA "revenant"
#                   <Gareth Coles> colesgareth2@hotmail.com AKA "gdude2002"
#
#    And,
#
#    The iCraft team:
#                   <Andrew Caluzzi> tehcid@gmail.com AKA "tehcid"
#                   <Andrew Dolgov> fox@bah.org.ru AKA "gothfox"
#                   <Andrew Horn> Andrew@GJOCommunity.com AKA "AndrewPH"
#                   <Brad Reardon> brad@bradness.co.cc AKA "PixelEater"
#                   <Clay Sweetser> CDBKJmom@aol.com AKA "Varriount"
#                   <James Kirslis> james@helplarge.com AKA "iKJames"
#                   <Jason Sayre> admin@erronjason.com AKA "erronjason"
#                   <Jonathon Dunford> sk8rjwd@yahoo.com AKA "sk8rjwd"
#                   <Joseph Connor> destroyerx100@gmail.com AKA "destroyerx1"
#                   <Kamyla Silva> supdawgyo@hotmail.com AKA "NotMeh"
#                   <Kristjan Gunnarsson> kristjang@ffsn.is AKA "eugo"
#                   <Nathan Coulombe> NathanCoulombe@hotmail.com AKA "Saanix"
#                   <Nick Tolrud> ntolrud@yahoo.com AKA "ntfwc"
#                   <Noel Benzinger> ronnygmod@gmail.com AKA "Dwarfy"
#                   <Randy Lyne> qcksilverdragon@gmail.com AKA "goober"
#                   <Willem van der Ploeg> willempieeploeg@live.nl AKA "willempiee"
#
#    Disclaimer: Parts of this code may have been contributed by the end-users.
#
#    iCraft is licensed under the Creative Commons
#    Attribution-NonCommercial-ShareAlike 3.0 Unported License. 
#    To view a copy of this license, visit http://creativecommons.org/licenses/by-nc-sa/3.0/
#    Or, send a letter to Creative Commons, 171 2nd Street,
#    Suite 300, San Francisco, California, 94105, USA.

import random, os
from core.plugins import ProtocolPlugin
from core.decorators import *
from core.constants import *
from core.globals import *

class helpPlugin(ProtocolPlugin):

    commands = {
        "help": "commandHelp",
        "?": "commandHelp",
        "cmdlist": "commandCmdlist",
        "commands": "commandCmdlist",
        "about": "commandAbout",
        "info": "commandAbout",
        "credits": "commandCredits",
        "motd": "commandMOTD",
        "greeting": "commandMOTD",
        "rules": "commandRules",
    }

    @info_list
    def commandHelp(self, parts, fromloc, overriderank):
        "/help [document/command] - Guest\nHelp for this server and commands."
        if len(parts) > 1:
            try:
                func = self.client.commands[parts[1].lower()]
            except KeyError:
                if parts[1].lower() == "chats":
                    self.client.sendServerMessage("Help; Chats")
                    self.client.sendServerMessage("Whispers: @username Whispers")    
                    self.client.sendServerMessage("WorldChat: !message")
                    if self.client.isModPlus():
                        self.client.sendServerMessage("StaffChat: #message")
                        self.client.sendServerMessage("ModChat: -message")
                    if self.client.isAdminPlus():
                        self.client.sendServerMessage("AdminChat: +message")
                    if self.client.isCoderPlus():
                        self.client.sendServerMessage("CoderChat: =message")
                    if self.client.isDirectorPlus():
                        self.client.sendServerMessage("DirectorChat: $message")
                elif parts[1].lower() == "physic":
                    self.client.sendServerMessage("Help; Physics Engine")
                    self.client.sendServerMessage("Turn physics on to use Physics (max of 5 worlds)")
                    self.client.sendServerMessage("If fwater is on then your water won't move.")
                    self.client.sendServerMessage("Orange blocks make Lavafalls, darkblue blocks make Waterfalls.")
                    self.client.sendServerMessage("Spouts need fwater to be on in order to work.")
                    self.client.sendServerMessage("Sand will fall, grass will grow, sponges will absorb.")
                    self.client.sendServerMessage("Use unflood to move all water, lava, and spouts from the world.")
                elif parts[1].lower() == "ranks":
                    self.client.sendNormalMessage(COLOUR_YELLOW+"Help: Server Ranks - "+COLOUR_DARKRED+"Owner/Console [9] "+COLOUR_GREEN+"Director [8] "+COLOUR_DARKPURPLE+"Coder [7] "+COLOUR_RED+"Admin [7] "+COLOUR_BLUE+"Mod [6] "+COLOUR_DARKYELLOW+"World Owner [5] "+COLOUR_DARKCYAN+"Op [4] "+COLOUR_CYAN+"Builder [3] "+COLOUR_GREY+"Member [2] "+COLOUR_WHITE+"Guest [1] "+COLOUR_BLACK+"Spec [0]")
                elif parts[1].lower() == "cc":
                    self.client.sendServerMessage("Help; Color Codes")
                    self.client.sendNormalMessage("&a%a &b%b &c%c &d%d &e%e &f%f")
                    self.client.sendNormalMessage("&0%0 &1%1 &2%2 &3%3 &4%4 &5%5 &6%6 &7%7 &8%8 &9%9")
                elif parts[1].lower() == "guide":
                    self.client.sendServerMessage("Help; The Guide")
                    self.client.sendServerMessage("/command required [optional]")
                    self.client.sendServerMessage("command - the command you're using (like /help)")
                    self.client.sendServerMessage("required - this stuff is required after the command")
                    self.client.sendServerMessage("optional - this stuff isn't needed, like blb coords")
                    self.client.sendServerMessage("Example: /help [document/command]")
                    self.client.sendServerMessage("You can do /help only or optionally input more.")
                else:
                    self.client.sendErrorMessage("Unknown command '%s'" % parts[1])
            else:
                if func.__doc__:
                    for line in func.__doc__.split("\n"):
                        self.client.sendServerMessage(line)
                else:
                    self.client.sendErrorMessage("There's no help for that command.")
        else:
            self.client.sendServerMessage("The Central Help Hub")
            self.client.sendServerMessage("Documents: /help [cc|chats|guide|physic|ranks]")
            self.client.sendServerMessage("Commands: /cmdlist - Lookup: /help command")
            self.client.sendServerMessage("About: /about - Credits: /credits")
            self.client.sendServerMessage("MOTD: /motd - Rules: /rules")

    @info_list
    def commandCmdlist(self, parts, fromloc, overriderank):
        "/cmdlist category - Guest\nThe command list of your rank, categories."
        if len(parts) > 1:
            if parts[1].lower() == "all" and not self.client.isModPlus():
                self.ListCommands("all")
            elif parts[1].lower() == "build":
                self.ListCommands("build")
            elif parts[1].lower() == "world":
                self.ListCommands("world")
            elif parts[1].lower() == "player":
                self.ListCommands("player")
            elif parts[1].lower() == "info":
                self.ListCommands("info")
            elif parts[1].lower() == "other":
                self.ListCommands("other")
            else:
                self.client.sendServerMessage("Unknown cmdlist '%s'" % parts[1])
        else:
            self.client.sendServerMessage("Command List - Use: /cmdlist category")
            self.client.sendServerMessage("Categories: build world player info other")

    def ListCommands(self,list):
        self.client.sendServerMessage("%s Commands:"%list.title())
        commands = []
        for name, command in self.client.commands.items():
            if not list == "other":
                if not list == "all":
                    if not getattr(command, "%s_list"%list, False):
                        continue
            else:
                if getattr(command, "plugin_list", False):
                    continue
                if getattr(command, "info_list", False):
                    continue
                if getattr(command, "build_list", False):
                    continue
                if getattr(command, "player_list", False):
                    continue
                if getattr(command, "world_list", False):
                    continue
            if getattr(command, "owner_only", False) and not self.client.isServerOwner():
                continue
            if getattr(command, "director_only", False) and not self.client.isDirectorPlus():
                continue
            if getattr(command, "coder_only", False) and not self.client.isCoderPlus():
                continue
            if getattr(command, "admin_only", False) and not self.client.isAdminPlus():
                continue
            if getattr(command, "mod_only", False) and not self.client.isModPlus():
                continue
            if getattr(command, "worldowner_only", False) and not self.client.isWorldOwnerPlus():
                continue
            if getattr(command, "op_only", False) and not self.client.isOpPlus():
                continue
            if getattr(command, "builder_only", False) and not self.client.isBuilderPlus():
                continue
            if getattr(command, "member_only", False) and not self.client.isMemberPlus():
                continue
            commands.append(name)
        if commands:
            self.client.sendServerList(sorted(commands))

    @info_list
    def commandAbout(self, parts, fromloc, overriderank):
        "/about - Guest\nAliases: info\nAbout the server and software."
        self.client.sendSplitServerMessage("About The Server, powered by iCraft+ %s | Credits: /credits" % VERSION)
        self.client.sendSplitServerMessage("Name: "+self.client.factory.server_name+"; owned by "+self.client.factory.owner)
        self.client.sendSplitServerMessage(self.client.factory.server_message)
        self.client.sendServerMessage("URL: "+self.client.factory.info_url)
        if self.client.factory.use_irc:
            if self.client.factory.irc_config.get("irc", "server") == "bots.esper.net":
                self.client.sendServerMessage("IRC: irc.esper.net "+self.client.factory.irc_channel)
            else:
                self.client.sendServerMessage("IRC: "+self.client.factory.irc_config.get("irc", "server")+" "+self.client.factory.irc_channel)

    @info_list
    def commandCredits(self, parts, fromloc, overriderank):
        "/credits - Guest\nCredits for the creators, devs and testers."
        self.client.sendServerMessage("iCraft Credits")
        list = Credits()
        for each in list:
            self.client.sendSplitServerMessage(each)

    @info_list
    def commandMOTD(self, parts, fromloc, overriderank):
        "/motd - Guest\nAliases: greeting\nShows the greeting."
        self.client.sendServerMessage("MOTD for "+self.client.factory.server_name+":")
        try:
            r = open('config/greeting.txt', 'r')
        except:
            r = open('config/greeting.example.txt', 'r')
        for line in r:
            self.client.sendNormalMessage(line)

    @info_list
    def commandRules(self, parts, fromloc, overriderank):
        "/rules - Guest\nShows the server rules."
        self.client.sendServerMessage("Rules for "+self.client.factory.server_name+":")
        try:
            r = open('config/rules.txt', 'r')
        except:
            r = open('config/rules.example.txt', 'r')
        for line in r:
            self.client.sendNormalMessage(line)
