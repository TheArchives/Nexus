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
#    Suite 300, San Francisco, California, 94105, USA

import urllib2, time, logging, os, re, sys, datetime, shutil, traceback, threading, gc, hashlib, random, cPickle
from urllib import urlencode
from core.console import StdinPlugin
from Queue import Queue, Empty
from reqs.twisted.internet.protocol import Factory
from reqs.twisted.internet import reactor
from ConfigParser import RawConfigParser as ConfigParser
from core.protocol import CoreServerProtocol
from core.world import World
from core.heartbeat import Heartbeat
from core.irc_client import ChatBotFactory
from core.constants import *
from core.plugins import *
from core.timer import ResettableTimer

class CoreFactory(Factory):
    """
    Factory that deals with the general world actions and cross-user comms.
    """
    protocol = CoreServerProtocol
    
    def reloadIrcBot(self):
        if(self.irc_relay):
            try:
                self.irc_relay.quit("Reloading the IRC Bot...")
                global ChatBotFactory
                del ChatBotFactory
                from core.irc_client import ChatBotFactory
                if self.ircbot and self.use_irc:
                    self.irc_config.read("config/irc.conf")             # Make sure to re-read the config
                    self.irc_nick = self.irc_config.get("irc", "nick")
                    self.irc_pass = self.irc_config.get("irc", "password")
                    self.irc_channel = self.irc_config.get("irc", "channel")
                    self.staffchat_channel = self.irc_config.get("irc", "staffchannel")
                    self.irc_cmdlogs = self.irc_config.getboolean("irc", "cmdlogs")
                    self.ircbot = self.irc_config.getboolean("irc", "ircbot")
                    self.staffchat = self.irc_config.getboolean("irc", "staffchat")
                    self.irc_relay = ChatBotFactory(self)
                    if self.ircbot and not (self.irc_channel == "#icraft" or self.irc_channel == "#channel") and not self.irc_nick == "botname":
                        if self.use_backup_irc:
                            reactor.connectTCP(self.irc_config.get("irc", "server2"), self.irc_config.getint("irc", "port"), self.irc_relay)
                        else:
                            reactor.connectTCP(self.irc_config.get("irc", "server"), self.irc_config.getint("irc", "port"), self.irc_relay)
                    else:
                        self.logger.error("IRC Bot failed to connect, you could modify, rename or remove irc.conf")
                        self.logger.error("You need to change your 'botname' and 'channel' fields to fix this error or turn the bot off by disabling 'ircbot'")
                    return True
            except:
                self.logger.error("Failed to reload the IRC Bot.")
                return False
        return False

    def reloadConfig(self):
        try:
            # TODO: Figure out which of these would work dynamically, otherwise delete them from this area.
            self.owner = self.config.get("main", "owner").lower()
            self.duplicate_logins = self.options_config.getboolean("options", "duplicate_logins")
            self.info_url = self.options_config.get("options", "info_url")
            self.away_kick = self.options_config.getboolean("options", "away_kick")
            self.away_time = self.options_config.getint("options", "away_time")
            self.colors = self.options_config.getboolean("options", "colors")
            self.physics_limit = self.options_config.getint("worlds", "physics_limit")
            self.default_backup = self.options_config.get("worlds", "default_backup")
            self.asd_delay = self.options_config.getint("worlds", "asd_delay")
            self.gchat = self.options_config.getboolean("worlds", "gchat")
            self.grief_blocks = self.ploptions_config.getint("antigrief", "blocks")
            self.grief_time = self.ploptions_config.getint("antigrief", "time")
            self.backup_freq = self.ploptions_config.getint("backups", "backup_freq")
            self.backup_default = self.ploptions_config.getboolean("backups", "backup_default")
            self.backup_max = self.ploptions_config.getint("backups", "backup_max")
            self.backup_auto = self.ploptions_config.getboolean("backups", "backup_auto")
            self.enable_archives = self.ploptions_config.getboolean("archiver", "enable_archiver")
            self.currency = self.ploptions_config.get("bank", "currency")
            self.build_hidden = self.ploptions_config.get("build","director")
            self.build_director = self.ploptions_config.get("build", "director")
            self.build_coder = self.ploptions_config.get("build", "admin")
            self.build_admin = self.ploptions_config.get("build", "admin")
            self.build_mod = self.ploptions_config.get("build", "mod")
            self.build_op = self.ploptions_config.get("build", "op")
            self.build_other = self.ploptions_config.get("build", "other")
            if self.backup_auto:
                reactor.callLater(float(self.backup_freq * 60),self.AutoBackup)
        except:
            return False

    def __init__(self):
        self.logger = logging.getLogger("Server")
        self.ServerVars = dict()
        self.specs = ConfigParser()
        self.last_heartbeat = time.time()
        self.lastseen = ConfigParser()
        self.config = ConfigParser()
        self.options_config = ConfigParser()
        self.ploptions_config = ConfigParser()
        self.wordfilter = ConfigParser()
        self.save_count = 1
        try:
            self.config.read("config/main.conf")
        except:
            self.logger.error("Something is messed up with your main.conf file. (Did you edit it in Notepad?)")
            sys.exit(1)
        try:
            self.options_config.read("config/options.conf")
        except:
            self.logger.error("Something is messed up with your options.conf file. (Did you edit it in Notepad?)")
            sys.exit(1)
        try:
            self.ploptions_config.read("config/ploptions.conf")
        except:
            self.logger.error("Something is messed up with your ploptions.conf file. (Did you edit it in Notepad?)")
            sys.exit(1)
        self.use_irc = False
        if  (os.path.exists("config/irc.conf")):
            self.use_irc = True
            self.irc_config = ConfigParser()
            try:
                self.irc_config.read("config/irc.conf")
            except:
                self.logger.error("Something is messed up with your irc.conf file. (Did you edit it in Notepad?)")
                sys.exit(1)
        self.saving = False
        try:
            self.max_clients = self.config.getint("main", "max_clients")
            self.server_message = self.config.get("main", "description")
            self.public = self.config.getboolean("main", "public")
            self.controller_port = self.config.get("network", "controller_port")
            self.controller_password = self.config.get("network", "controller_password")
            self.server_name = self.config.get("main", "name")
            if self.server_name == "iCraft Server":
                self.logger.error("You forgot to give your server a name.")
            self.owner = self.config.get("main", "owner").lower()
            if self.owner == "yournamehere":
                self.logger.error("You forgot to make yourself the server owner.")
            self.server_port = self.config.getint("network", "port")
            self.heartbeat_url = "http://www.minecraft.net/heartbeat.jsp"            # alternatively https://direct.worldofminecraft.com/hb.php if you think it'll work
            self.use_second_heartbeat = False
            if self.config.has_section("heartbeat"):
                if self.config.has_option("heartbeat", "url"):
                    self.heartbeat_url = self.config.get("heartbeat", "url")
                if self.config.has_option("heartbeat", "name2"):
                    self.server_name2 = self.config.get("heartbeat", "name2")
                    self.server_port2 = self.config.getint("heartbeat", "port2")
                    self.use_second_heartbeat = True
            self.salt = ""
            if self.config.has_option("main", "salt"):
                self.salt = self.config.get("main", "salt")
        except:
            self.logger.error(traceback.format_exc())
            self.logger.error("You don't have a main.conf file! You need to rename main.example.conf to main.conf")
            sys.exit(1)
        try:
            self.duplicate_logins = self.options_config.getboolean("options", "duplicate_logins")
            self.info_url = self.options_config.get("options", "info_url")
            self.away_kick = self.options_config.getboolean("options", "away_kick")
            self.away_time = self.options_config.getint("options", "away_time")
            self.colors = self.options_config.getboolean("options", "colors")
            self.physics_limit = self.options_config.getint("worlds", "physics_limit")
            self.default_name = self.options_config.get("worlds", "default_name")
            self.default_backup = self.options_config.get("worlds", "default_backup")
            self.asd_delay = self.options_config.getint("worlds", "asd_delay")
            self.gchat = self.options_config.getboolean("worlds", "gchat")
        except:
            self.logger.error("You don't have a options.conf file! You need to rename options.example.conf to options.conf")
            sys.exit(1)
        try:
            self.grief_blocks = self.ploptions_config.getint("antigrief", "blocks")
            self.grief_time = self.ploptions_config.getint("antigrief", "time")
            self.backup_freq = self.ploptions_config.getint("backups", "backup_freq")
            self.backup_default = self.ploptions_config.getboolean("backups", "backup_default")
            self.backup_max = self.ploptions_config.getint("backups", "backup_max")
            self.backup_auto = self.ploptions_config.getboolean("backups", "backup_auto")
            self.enable_archives = self.ploptions_config.getboolean("archiver", "enable_archiver")
            self.currency = self.ploptions_config.get("bank", "currency")
            self.build_hidden = self.ploptions_config.get("build", "director")
            self.build_director = self.ploptions_config.get("build", "director")
            self.build_coder = self.ploptions_config.get("build", "admin")
            self.build_admin = self.ploptions_config.get("build", "admin")
            self.build_mod = self.ploptions_config.get("build", "mod")
            self.build_op = self.ploptions_config.get("build", "op")
            self.build_other = self.ploptions_config.get("build", "other")
            if self.backup_auto:
                reactor.callLater(float(self.backup_freq * 60),self.AutoBackup)
        except:
            self.logger.error("You don't have a ploptions.conf file! You need to rename ploptions.example.conf to ploptions.conf")
            sys.exit(1)
        if self.use_irc:
            self.irc_nick = self.irc_config.get("irc", "nick")
            self.irc_pass = self.irc_config.get("irc", "password")
            self.irc_channel = self.irc_config.get("irc", "channel")
            self.staffchat_channel = self.irc_config.get("irc", "staffchannel")
            self.irc_cmdlogs = self.irc_config.getboolean("irc", "cmdlogs")
            self.ircbot = self.irc_config.getboolean("irc", "ircbot")
            self.staffchat = self.irc_config.getboolean("irc", "staffchat")
            self.irc_relay = ChatBotFactory(self)
            self.use_backup_irc = False
            if self.ircbot and not (self.irc_channel == "#icraft" or self.irc_channel == "#channel") and not self.irc_nick == "botname":
                reactor.connectTCP(self.irc_config.get("irc", "server"), self.irc_config.getint("irc", "port"), self.irc_relay)
            else:
                self.logger.error("IRC Bot failed to connect, you could modify, rename or remove irc.conf")
                self.logger.error("You need to change your 'botname' and 'channel' fields to fix this error or turn the bot off by disabling 'ircbot'")
        else:
            self.irc_relay = None
        self.default_loaded = False
        # Word Filter
        try:
            self.wordfilter.read("config/wordfilter.conf")
        except:
            self.logger.error("Something is messed up with your wordfilter.conf file. (Did you edit it in Notepad?)")
            sys.exit(1)
        self.filter = []
        try:
            number = int(self.wordfilter.get("filter", "count"))
        except:
            self.logger.error("You need to rename wordfilter.example.conf to wordfilter.conf")
            sys.exit(1)
        for x in range(number):
            self.filter = self.filter + [[self.wordfilter.get("filter","s"+str(x)),self.wordfilter.get("filter","r"+str(x))]]
        # Salt, for the heartbeat server/verify-names
        if len(self.salt) == 0:
            self.salt = hashlib.md5(hashlib.md5(str(random.getrandbits(128))).digest()).hexdigest()[-32:].strip("0")
        # Load up the plugins specified
        self.plugins_config = ConfigParser()
        try:
            self.plugins_config.read("config/plugins.conf")
        except:
            self.logger.error("Something is messed up with your plugins.conf file. (Did you edit it in Notepad?)")
            sys.exit(1)
        try:
            plugins = self.plugins_config.options("plugins")
        except:
            print ("NOTICE: You need to rename plugins.example.conf to plugins.conf")
            sys.exit(1)
        self.logger.info("Loading plugins...")
        load_plugins(plugins)
        # Open the chat log, ready for appending
        self.chatlog = open("logs/chat.log", "a")
        self.adlog = open("logs/staff.log", "a")
        # Create a default world, if there isn't one.
        if not os.path.isdir("worlds/%s" % self.default_name):
            self.logger.info("Generating %s world..." % self.default_name)
            self.createWorld(self.default_name, 64, 64, 64)
            self.logger.info("Generated.")
        # Initialise internal datastructures
        self.worlds = {}
        self.hidden = set()
        self.directors = set()
        self.coders = set()
        self.admins = set()
        self.mods = set()
        self.globalbuilders = set()
        self.members = set()
        self.spectators = set()
        self.silenced = set()
        self.worldowners = {}
        self.banned = {}
        self.ipbanned = {}
        self.lastseen = {}
        # Load up the contents of those.
        self.loadMeta()
        # Set up a few more things.
        self.queue = Queue()
        self.clients = {}
        self.usernames = {}
        self.console = StdinPlugin(self)
        self.console.start()
        self.heartbeat = Heartbeat(self)
        # Boot worlds that got loaded
        for world in self.worlds:
            self.loadWorld("worlds/%s" % world, world)
        # Set up tasks to run during execution
        reactor.callLater(0.1, self.sendMessages)
        reactor.callLater(1, self.printInfo)
        # Initial startup is instant, but it updates every 10 minutes.
        self.world_save_stack = []
        reactor.callLater(60, self.saveWorlds)
        if self.enable_archives:
            if "archives" not in protocol_plugins:
                self.loadPlugin('archives')
            reactor.callLater(1, self.loadArchives)
        if self.backup_auto:
            reactor.callLater(float(self.backup_freq * 60), self.AutoBackup)
        gc.disable()
        self.cleanGarbage()

    def cleanGarbage(self):
        count = gc.collect()
        self.logger.info("%i garbage objects collected, %i were uncollected." % ( count, len(gc.garbage)))
        reactor.callLater(60*15, self.cleanGarbage)

    def loadMeta(self):
        "Loads the 'meta' - variables that change with the server (worlds, admins, etc.)"
        config = ConfigParser()
        config.read("config/data/ranks.meta")
        specs = ConfigParser()
        specs.read("config/data/spectators.meta")
        # Read in the coders
        if config.has_section("coders"):
            for name in config.options("coders"):
                self.coders.add(name)
        # Read in the admins
        if config.has_section("admins"):
            for name in config.options("admins"):
                self.admins.add(name)
        # Read in the mods
        if config.has_section("mods"):
            for name in config.options("mods"):
                self.mods.add(name)
        if config.has_section("globalbuilders"):
            for name in config.options("globalbuilders"):
                self.globalbuilders.add(name)
        if config.has_section("members"):
            for name in config.options("members"):
                self.members.add(name)
        # Read in the hidden
        if config.has_section("hidden"):
            for name in config.options("hidden"):
                self.hidden.add(name)
        # Read in the directors
        if config.has_section("directors"):
            for name in config.options("directors"):
                self.directors.add(name)
        if config.has_section("silenced"):
            for name in config.options("silenced"):
                self.silenced.add(name)
        # Read in the spectators (experimental)
        if specs.has_section("spectators"):
            for name in specs.options("spectators"):
                self.spectators.add(name)
        # Read in the bans and ipbans
        bans = ConfigParser()
        bans.read("config/data/bans.meta")
        if bans.has_section("banned"):
            for name in bans.options("banned"):
                self.banned[name] = bans.get("banned", name)
        if bans.has_section("ipbanned"):
            for ip in bans.options("ipbanned"):
                self.ipbanned[ip] = bans.get("ipbanned", ip)
        # Read in the lastseen
        lastseen = ConfigParser()
        lastseen.read("config/data/lastseen.meta")
        if lastseen.has_section("lastseen"):
            for username in lastseen.options("lastseen"):
                self.lastseen[username] = lastseen.getfloat("lastseen", username)
        # Read in the worlds
        worlds = ConfigParser()
        worlds.read("config/data/worlds.meta")
        if worlds.has_section("worlds"):
            for name in worlds.options("worlds"):
                if name is self.default_name:
                    self.default_loaded = True
        else:
            self.worlds[self.default_name] = None
        if not self.default_loaded:
            self.worlds[self.default_name] = None
        # Read in the index of world owners
        if os.path.exists('config/data/worldowners.dat'):
            fileOwners = open('config/data/worldowners.dat', 'r')
            self.worldowners = cPickle.load(fileOwners)
            fileOwners.close()

    def saveMeta(self):
        "Saves the server's meta back to a file."
        config = ConfigParser()
        specs = ConfigParser()
        lastseen = ConfigParser()
        bans = ConfigParser()
        worlds = ConfigParser()
        # Make the sections
        config.add_section("hidden")
        config.add_section("directors")
        config.add_section("admins")
        config.add_section("coders")
        config.add_section("mods")
        config.add_section("globalbuilders")
        config.add_section("members")
        config.add_section("silenced")
        bans.add_section("banned")
        bans.add_section("ipbanned")
        specs.add_section("spectators")
        lastseen.add_section("lastseen")
        # Write out things
        for hidden in self.hidden:
            config.set("hidden", hidden, "true")
        for director in self.directors:
            config.set("directors", director, "true")
        for coder in self.coders:
            config.set("coders", coder, "true")
        for admin in self.admins:
            config.set("admins", admin, "true")
        for mod in self.mods:
            config.set("mods", mod, "true")
        for globalbuilder in self.globalbuilders:
            config.set("globalbuilders", globalbuilder, "true")
        for member in self.members:
            config.set("members", member, "true")
        for ban, reason in self.banned.items():
            bans.set("banned", ban, reason)
        for spectator in self.spectators:
            specs.set("spectators", spectator, "true")
        for silence in self.silenced:
            config.set("silenced", silence, "true")
        for ipban, reason in self.ipbanned.items():
            bans.set("ipbanned", ipban, reason)
        for username, ls in self.lastseen.items():
            lastseen.set("lastseen", username, str(ls))
        fp = open("config/data/ranks.meta", "w")
        config.write(fp)
        fp.close()
        fp = open("config/data/spectators.meta", "w")
        specs.write(fp)
        fp.close()
        fp = open("config/data/lastseen.meta", "w")
        lastseen.write(fp)
        fp.close()
        fp = open("config/data/bans.meta", "w")
        bans.write(fp)
        fp.close()
        fp = open("config/data/worlds.meta", "w")
        worlds.write(fp)
        fp.close()
        fp = open('config/data/worldowners.dat', 'w')
        cPickle.dump(self.worldowners, fp)
        fp.close()

    def printInfo(self):
        self.logger.info("There are %s users on the server" % len(self.clients))
        for key in self.worlds:
            self.logger.info("%s: %s" % (key, ", ".join(str(c.username) for c in self.worlds[key].clients)))
        #if (time.time() - self.last_heartbeat) > 180:
        #    self.heartbeat = None
        #    self.heartbeat = Heartbeat(self)       #TODO Fish: We shouldn't (hopefully) need this anymore. Also it should be done differently given how I revised Heartbeat.
        reactor.callLater(60, self.printInfo)

    def loadArchive(self, filename):
        "Boots an archive given a filename. Returns the new world ID."
        # Get an unused world name
        i = 1
        while self.world_exists("a-%i" % i):
            i += 1
        world_id = "a-%i" % i
        # Copy and boot
        self.newWorld(world_id, "../core/archives/%s" % filename)
        self.loadWorld("worlds/%s" % world_id, world_id)
        world = self.worlds[world_id]
        world.is_archive = True
        return world_id

    def saveWorlds(self):
        "Saves the worlds, one at a time, with a 1 second delay."
        if not self.saving:
            if not self.world_save_stack:
                self.world_save_stack = list(self.worlds)
            key = self.world_save_stack.pop()
            self.saveWorld(key)
            if not self.world_save_stack:
                reactor.callLater(60, self.saveWorlds)
                self.saveMeta()
            else:
                reactor.callLater(1, self.saveWorlds)

    def saveWorld(self, world_id,shutdown = False):
        try:
            world = self.worlds[world_id]
            world.save_meta()
            world.flush()
            self.logger.info("World '%s' has been saved." % world_id)
            if self.save_count == 5:
                for client in list(list(self.worlds[world_id].clients))[:]:
                    client.sendServerMessage("[%s] World '%s' has been saved." % (datetime.datetime.utcnow().strftime("%H:%M"), world_id))
                self.save_count = 1
            else:
                self.save_count += 1
            if shutdown: del self.worlds[world_id]
        except:
            self.logger.info("Error saving %s" % world_id)

    def claimId(self, client):
        for i in range(1, self.max_clients+1):
            if i not in self.clients:
                self.clients[i] = client
                return i
        raise ServerFull

    def releaseId(self, id):
        del self.clients[id]

    def joinWorld(self, worldid, user):
        "Makes the user join the given World."
        new_world = self.worlds[worldid]
        try:
            self.logger.info("%s is joining world %s" %(user.username,new_world.basename))
        except:
            self.logger.info("%s is joining world %s" %(user.transport.getPeer().host,new_world.basename))
        if hasattr(user, "world") and user.world:
            self.leaveWorld(user.world, user)
        user.world = new_world
        new_world.clients.add(user)
        if not worldid == self.default_name and not new_world.ASD == None:
            new_world.ASD.kill()
            new_world.ASD = None
        return new_world

    def leaveWorld(self, world, user):
        world.clients.remove(user)
        if world.autoshutdown and len(world.clients)<1:
            if world.basename == ("worlds/" + self.default_name):
                return
            else:
                if not self.asd_delay == 0:
                    world.ASD = ResettableTimer(self.asd_delay*60,1,world.unload)
                else:
                    world.ASD = ResettableTimer(30,1,world.unload)
                world.ASD.start()

    def loadWorld(self, filename, world_id):
        """
        Loads the given world file under the given world ID, or a random one.
        Returns the ID of the new world.
        """
        world = self.worlds[world_id] =  World(filename)
        world.source = filename
        world.clients = set()
        world.id = world_id
        world.factory = self
        world.start()
        self.logger.info("World '%s' Booted." % world_id)
        return world_id

    def unloadWorld(self, world_id,ASD=False):
        """
        Unloads the given world ID.
        """
        try:
            if ASD and len(self.worlds[world_id].clients)>0:
                self.worlds[world_id].ASD.kill()
                self.worlds[world_id].ASD = None
                return
        except KeyError:
            return
        try:
            assert world_id != self.default_name
        except:
            self.client.sendServerMessage("You can't shutdown %s." % self.default_name)
        if not self.worlds[world_id].ASD == None:
            self.worlds[world_id].ASD.kill()
            self.worlds[world_id].ASD = None
        for client in list(list(self.worlds[world_id].clients))[:]:
            client.changeToWorld(self.default_name)
            client.sendServerMessage("World '%s' has been Shutdown." % world_id)
        self.worlds[world_id].stop()
        self.saveWorld(world_id,True)
        self.logger.info("World '%s' Shutdown." % world_id)

    def rebootWorld(self, world_id):
        """
        Reboots a world in a crash case
        """
        for client in list(list(self.worlds[world_id].clients))[:]:
            if world_id == self.default_name:
                client.loadWorld("worlds/%s" % world_id, world_id)
                client.changeToWorld(self.default_backup)
            else:
                client.changeToWorld(self.default_name)
            client.sendServerMessage("%s has been Rebooted" % world_id)
        self.worlds[world_id].stop()
        self.worlds[world_id].flush()
        self.worlds[world_id].save_meta()
        del self.worlds[world_id]
        world = self.worlds[world_id] =  World("worlds/%s" % world_id, world_id)
        world.source = "worlds/" + world_id
        world.clients = set()
        world.id = world_id
        world.factory = self
        world.start()
        self.logger.info("Rebooted %s" % world_id)

    def publicWorlds(self):
        """
        Returns the IDs of all public worlds
        """
        for world_id, world in self.worlds.items():
            if not world.private:
                yield world_id

    def recordPresence(self, username):
        """
        Records a sighting of 'username' in the lastseen dict.
        """
        self.lastseen[username.lower()] = time.time()

    def unloadPlugin(self, plugin_name):
        "Reloads the plugin with the given module name."
        # Unload the plugin from everywhere
        for plugin in plugins_by_module_name(plugin_name):
            if issubclass(plugin, ProtocolPlugin):
                for client in self.clients.values():
                    client.unloadPlugin(plugin)
        # Unload it
        unload_plugin(plugin_name)

    def loadPlugin(self, plugin_name):
        # Load it
        load_plugin(plugin_name)
        # Load it back into clients etc.
        for plugin in plugins_by_module_name(plugin_name):
            if issubclass(plugin, ProtocolPlugin):
                for client in self.clients.values():
                    client.loadPlugin(plugin)

    def sendMessages(self):
        "Sends all queued messages, and lets worlds recieve theirs."
        try:
            while True:
                # Get the next task
                source_client, task, data = self.queue.get_nowait()
                try:
                    if isinstance(source_client, World):
                        world = source_client
                    elif str(source_client).startswith("<StdinPlugin"):
                        world = self.worlds[self.default_name]
                    elif task != TASK_SERVERURGENTMESSAGE:      # Some messages don't need a World.
                        try:
                            world = source_client.world
                        except AttributeError:
                            self.logger.warn("Source client for message has no world. Ignoring.")
                            continue
                    # Someone built/deleted a block
                    if task is TASK_BLOCKSET:
                        # Only run it for clients who weren't the source.
                        for client in world.clients:
                            if client is not source_client:
                                client.sendBlock(*data)
                    # Someone moved
                    elif task is TASK_PLAYERPOS:
                        # Only run it for clients who weren't the source.
                        for client in world.clients:
                            if client != source_client:
                                client.sendPlayerPos(*data)
                    # Someone moved only their direction
                    elif task is TASK_PLAYERDIR:
                        # Only run it for clients who weren't the source.
                        for client in world.clients:
                            if client != source_client:
                                client.sendPlayerDir(*data)
                    # Someone finished a mass replace that requires respawn for everybody.
                    elif task is TASK_INSTANTRESPAWN:
                        for client in world.clients:
                            # Save their initial position
                            client.initial_position = client.x>>5, client.y>>5, client.z>>5, client.h
                            client.sendPlayerLeave(data)
                            client.loading_world = True
                            breakable_admins = client.runHook("canbreakadmin")
                            client.sendPacked(TYPE_INITIAL, 7, ("%s: %s" % (self.server_name, world.id)), "Respawning world '%s'..." % world.id, 100 if breakable_admins else 0)
                            client.sendLevel(slient=True)
                    # Someone spoke!
                    elif task is TASK_MESSAGE:
                        # More Word Filter
                        id, colour, username, text = data
                        if len(username) > 0 and username[0] == '&':
                            colour = ""     # don't use this colour since the username begins with a color code
                        text = self.messagestrip(text)
                        data = (id, colour, username, text)
                        for client in self.clients.values():
                            client.sendMessage(*data)
                        id, colour, username, text = data
                        self.logger.info("%s: %s" % (username, text))
                        self.chatlog.write("[%s] %s: %s\n" % (datetime.datetime.utcnow().strftime("%Y/%m/%d %H:%M:%S"), username, text))
                        self.chatlog.flush()
                        if self.irc_relay and world:
                            self.irc_relay.sendMessage(colour+username, text)
                    # Someone spoke!
                    elif task is TASK_IRCMESSAGE:
                        for client in self.clients.values():
                            client.sendMessage(*data)
                        id, colour, username, text = data
                        self.logger.info("<%s> %s" % (username, text))
                        self.chatlog.write("[%s] <%s> %s\n" % (datetime.datetime.utcnow().strftime("%Y/%m/%d %H:%M:%S"), username, text))
                        self.chatlog.flush()
                        if self.irc_relay and world:
                            self.irc_relay.sendMessage(colour+username, text)
                    # Someone actioned!
                    elif task is TASK_ACTION:
                        # More Word Filter
                        id, colour, username, text = data
                        text = self.messagestrip(text)
                        data = (id,colour,username,text)
                        for client in self.clients.values():
                            client.sendAction(*data)
                        id, colour, username, text = data
                        self.logger.info("* %s %s" % (username, text))
                        self.chatlog.write("[%s] * %s %s\n" % (datetime.datetime.utcnow().strftime("%Y/%m/%d %H:%M:%S"), username, text))
                        self.chatlog.flush()
                        if self.irc_relay and world:
                            self.irc_relay.sendAction(colour+username, ""+text)
                    # Someone connected to the server
                    elif task is TASK_PLAYERCONNECT:
                        for client in self.usernames:
                            self.usernames[client].sendNewPlayer(*data)
                            if self.username.lower() in INFO_VIPLIST and not self.isModPlus():
                                self.usernames[client].sendNormalMessage(COLOUR_DARKRED+"iCraft Developer spotted;")
                            self.usernames[client].sendServerMessage("%s[+] %s%s &ehas come online." % (COLOUR_DARKGREEN, source_client.userColor(), source_client.username))
                        if self.irc_relay and world:
                            if self.username.lower() in INFO_VIPLIST and not self.isModPlus():
                                self.irc_relay.sendServerMessage("04iCraft Developer spotted;")
                            if self.username.lower() in self.factory.owner:
                                self.irc_relay.sendServerMessage("3[+] 5%s 07has come online." % source_client.username)
                            elif self.username.lower() in self.factory.directors:
                                self.irc_relay.sendServerMessage("3[+] 9%s 07has come online." % source_client.username)
                            elif self.username.lower() in self.factory.admins:
                                self.irc_relay.sendServerMessage("3[+] 4%s 07has come online." % source_client.username)
                            elif self.username.lower() in self.factory.coders:
                                self.irc_relay.sendServerMessage("3[+] 6%s 07has come online." % source_client.username)
                            elif self.username.lower() in self.factory.mods:
                                self.irc_relay.sendServerMessage("3[+] 12%s 07has come online." % source_client.username)
                            elif self.username.lower() in self.factory.members:
                                self.irc_relay.sendServerMessage("3[+] 14%s 07has come online." % source_client.username)
                            elif self.username.lower() in self.world.owner:
                                self.irc_relay.sendServerMessage("3[+] 7%s has come online." % source_client.username)
                            elif self.username.lower() in self.world.ops:
                                self.irc_relay.sendServerMessage("3[+] 10%s 07has come online." % source_client.username)
                            elif self.username.lower() in self.world.builders:
                                self.irc_relay.sendServerMessage("3[+] 11%s 07has come online." % source_client.username)
                            else:
                                self.irc_relay.sendServerMessage("3[+] %s 07has come online." % source_client.username)
                    # Someone joined a world!
                    elif task is TASK_NEWPLAYER:
                        for client in world.clients:
                            if client != source_client:
                                client.sendNewPlayer(*data)
                            client.sendNormalMessage("%s[*] %s%s &ehas joined the world." % (COLOUR_DARKBLUE, source_client.userColour(), source_client.username))
                    # Someone left!
                    elif task is TASK_PLAYERLEAVE:
                        # Only run it for clients who weren't the source.
                        for client in self.clients.values():
                            client.sendPlayerLeave(*data)
                            if not source_client.username is None:
                                client.sendNormalMessage("%s[-] %s%s &ehas gone offline." % (COLOUR_DARKRED, source_client.userColour(), source_client.username))
                            else:
                                source_client.logger.warn("Pinged the server.")
                        if not source_client.username is None:
                            if self.irc_relay and world:
                                if source_client.username.lower() in self.owner:
                                    self.irc_relay.sendServerMessage("5[-] 5%s 07has gone offline." % source_client.username)
                                elif source_client.username.lower() in self.directors:
                                    self.irc_relay.sendServerMessage("5[-] 9%s 07has gone offline." % source_client.username)
                                elif source_client.username.lower() in self.coders:
                                    self.irc_relay.sendServerMessage("5[-] 6%s 07has gone offline." % source_client.username)
                                elif source_client.username.lower() in self.admins:
                                    self.irc_relay.sendServerMessage("5[-] 4%s 07has gone offline." % source_client.username)
                                elif source_client.username.lower() in self.mods:
                                    self.irc_relay.sendServerMessage("5[-] 12%s 07has gone offline." % source_client.username)
                                elif source_client.isWorldOwner():
                                    self.irc_relay.sendServerMessage("5[-] 7%s has gone offline." % source_client.username)
                                elif source_client.isOp():
                                    self.irc_relay.sendServerMessage("5[-] 10%s 07has gone offline." % source_client.username)
                                elif source_client.isBuilder():
                                    self.irc_relay.sendServerMessage("5[-] 11%s 07has gone offline." % source_client.username)
                                elif source_client.username.lower() in self.members:
                                    self.irc_relay.sendServerMessage("5[-] 14%s 07has gone offline." % source_client.username)
                                else:
                                    self.irc_relay.sendServerMessage("5[-] %s 07has gone offline." % source_client.username)
                    # Someone changed worlds!
                    elif task is TASK_WORLDCHANGE:
                        # Only run it for clients who weren't the source.
                        for client in data[1].clients:
                            client.sendPlayerLeave(data[0])
                            client.sendNormalMessage("%s[*] %s%s &ejoined '%s'" % (COLOUR_DARKBLUE, source_client.userColour(), source_client.username, world.id))
                        if self.irc_relay and world:
                            self.irc_relay.sendServerMessage("2[*] 07%s joined '%s'" % (source_client.username, world.id))
                        self.logger.info("%s has now joined '%s'" % (source_client.username, world.id))
                    elif task == TASK_STAFFMESSAGE:
                        # Give all staff the message :D
                        id, colour, username, text, IRC = data
                        message = self.messagestrip(text);
                        for user, client in self.usernames.items():
                            if self.isModPlus(user):
                                client.sendMessage(100, COLOUR_YELLOW+"#"+colour, username, message, False, False)
                        if self.staffchat and self.irc_relay and len(data)>3:
                            self.irc_relay.sendServerMessage("# "+colour+username+": "+text,admin=True)
                        self.logger.info("#"+username+": "+text)
                        self.adlog.write("["+datetime.datetime.utcnow().strftime("%Y/%m/%d %H:%M:%S")+"] #"+username+": "+text+"\n")
                        self.adlog.flush()
                    elif task == TASK_IRCSTAFFMESSAGE:
                        # Give all staff the message :D
                        id, colour, username, text, IRC = data
                        message = self.messagestrip(text);
                        for user, client in self.usernames.items():
                            if self.isModPlus(user):
                                client.sendMessage(100, COLOUR_YELLOW+"#"+colour, username, message, False, False)
                        self.logger.info("#"+username+": "+text)
                        self.adlog.write("["+datetime.datetime.utcnow().strftime("%Y/%m/%d %H:%M:%S")+"] #"+username+": "+text+"\n")
                        self.adlog.flush()
                    elif task == TASK_GLOBALMESSAGE:
                        # Give all world people the message
                        id, world, message = data
                        message = self.messagestrip(message);
                        for client in world.clients:
                            client.sendNormalMessage(message)
                    elif task == TASK_WORLDMESSAGE:
                        # Give all world people the message
                        id, world, message = data
                        for client in world.clients:
                            client.sendNormalMessage(message)
                    elif task == TASK_SERVERMESSAGE:
                        # Give all people the message
                        message = data
                        message = self.messagestrip(message);
                        for client in self.clients.values():
                            client.sendNormalMessage(COLOUR_DARKBLUE + message)
                        self.logger.info(message)
                        if self.irc_relay and world:
                            self.irc_relay.sendServerMessage(COLOUR_DARKBLUE + message)
                    elif task == TASK_ONMESSAGE:
                        # Give all people the message
                        id, world, text = data
                        message = self.messagestrip(text)
                        for client in self.clients.values():
                            client.sendNormalMessage(COLOUR_YELLOW + message)
                        if self.irc_relay and world:
                            self.irc_relay.sendServerMessage(COLOUR_YELLOW + message)
                    elif task == TASK_ADMINMESSAGE:
                        # Give all people the message
                        id, world, text = data
                        message = self.messagestrip(text)
                        for client in self.clients.values():
                            client.sendNormalMessage(COLOUR_YELLOW + message)
                        if self.irc_relay and world:
                            self.irc_relay.sendServerMessage(message)
                    elif task == TASK_PLAYERRESPAWN:
                        # We need to immediately respawn the user to update their nick.
                        for client in world.clients:
                            if client != source_client:
                                id, username, x, y, z, h, p = data
                                client.sendPlayerLeave(id)
                                client.sendNewPlayer(id, username, x, y, z, h, p)
                    elif task == TASK_SERVERURGENTMESSAGE:
                        # Give all people the message
                        message = data
                        for client in self.clients.values():
                            client.sendNormalMessage(COLOUR_DARKRED + message)
                        self.logger.info(message)
                        if self.irc_relay: #and world:      #TODO Fish: why was there a check for the world variable here?
                            self.irc_relay.sendServerMessage(COLOUR_DARKRED + message)
                    elif task == TASK_CYAN:
                        # Give all people the message
                        message = data
                        for client in self.clients.values():
                            client.sendNormalMessage(COLOUR_CYAN + message)
                        self.logger.info(message)
                        if self.irc_relay and world:
                            self.irc_relay.sendServerMessage(COLOUR_CYAN + message)
                    elif task == TASK_AWAYMESSAGE:
                        # Give all world people the message
                        message = data
                        for client in self.clients.values():
                            client.sendNormalMessage(COLOUR_DARKPURPLE + message)
                        self.logger.info("AWAY - %s" %message)
                        self.chatlog.write("[%s] %s %s\n" % (datetime.datetime.utcnow().strftime("%Y/%m/%d %H:%M:%S"), "", message))
                        self.chatlog.flush()
                        if self.irc_relay and world:
                            self.irc_relay.sendAction("", message)
                    elif task == TASK_INGAMEMESSAGE:
                        # Give all people the message
                        message = data
                        message = self.messagestrip(message);
                        for client in self.clients.values():
                            client.sendNormalMessage(COLOUR_YELLOW + message)
                        self.logger.info(message)
                        if self.irc_relay and world:
                            self.irc_relay.sendServerMessage(COLOUR_DARKYELLOW + message)
                    elif task == TASK_BLACK:
                        # Give all people the message
                        message = data
                        message = self.messagestrip(message);
                        for client in self.clients.values():
                            client.sendNormalMessage(COLOUR_BLACK + message)
                        self.logger.info(message)
                        if self.irc_relay and world:
                            self.irc_relay.sendServerMessage(COLOUR_BLACK+message)
                    elif task == TASK_GREEN:
                        # Give all people the message
                        message = data
                        message = self.messagestrip(message);
                        for client in self.clients.values():
                            client.sendNormalMessage(COLOUR_GREEN + message)
                        self.logger.info(message)
                        if self.irc_relay and world:
                            self.irc_relay.sendServerMessage(COLOUR_GREEN+message)
                    elif task == TASK_AWARD:
                        # Give all people the message
                        message = data
                        message = self.messagestrip(message);
                        for client in self.clients.values():
                            client.sendNormalMessage(COLOUR_DARKYELLOW + message)
                        self.logger.info(message)
                        if self.irc_relay and world:
                            self.irc_relay.sendServerMessage(COLOUR_DARKYELLOW+message)
                    elif task == TASK_OWNERMESSAGE:
                        # Give all people the message
                        message = data
                        message = self.messagestrip(message);
                        for client in self.clients.values():
                            client.sendNormalMessage(message)
                        self.logger.info(message)
                        if self.irc_relay and world:
                            self.irc_relay.sendServerMessage(message)
                    elif task == TASK_DIRECTORMESSAGE:
                        # Give all directors the message :D
                        id, colour, username, text, IRC = data
                        message = self.messagestrip(text);
                        for user, client in self.usernames.items():
                            if self.isDirectorPlus(user):
                                client.sendMessage(100, COLOUR_DARKGREEN+"$"+colour, username, message, False, False)
                        self.logger.info("$"+username+": "+text)
                        self.adlog.write("["+datetime.datetime.utcnow().strftime("%Y/%m/%d %H:%M:%S")+"] $"+username+": "+text+"\n")
                        self.adlog.flush()
                    elif task == TASK_MODMESSAGE:
                        # Give all staff but admins the message :D
                        id, colour, username, text, IRC = data
                        message = self.messagestrip(text);
                        for user, client in self.usernames.items():
                            if self.isMod(user) or self.isDirectorPlus(user):
                                client.sendMessage(100, COLOUR_DARKBLUE+"-"+colour, username, message, False, False)
                        self.logger.info("-"+username+": "+text)
                        self.adlog.write("["+datetime.datetime.utcnow().strftime("%Y/%m/%d %H:%M:%S")+"] -"+username+": "+text+"\n")
                        self.adlog.flush()
                    elif task == TASK_ADMINCHATMESSAGE:
                        # Give all admins+ the message :D
                        id, colour, username, text, IRC = data
                        message = self.messagestrip(text);
                        for user, client in self.usernames.items():
                            if self.isAdminPlus(user):
                                client.sendMessage(100, COLOUR_DARKRED+"+"+colour, username, message, False, False)
                        self.logger.info("+"+username+": "+text)
                        self.adlog.write("["+datetime.datetime.utcnow().strftime("%Y/%m/%d %H:%M:%S")+"] +"+username+": "+text+"\n")
                        self.adlog.flush()
                    elif task == TASK_CODERMESSAGE:
                        # Give all coders the message :D
                        id, colour, username, text, IRC = data
                        message = self.messagestrip(text);
                        for user, client in self.usernames.items():
                            if self.isCoderPlus(user):
                                client.sendMessage(100, COLOUR_PURPLE+"="+colour, username, message, False, False)
                        self.logger.info("="+username+": "+text)
                        self.adlog.write("["+datetime.datetime.utcnow().strftime("%Y/%m/%d %H:%M:%S")+"] ="+username+": "+text+"\n")
                        self.adlog.flush()
                except Exception, e:
                    self.logger.error(traceback.format_exc())
        except Empty:
            pass
        # OK, now, for every world, let them read their queues
        for world in self.worlds.values():
            world.read_queue()
        # Come back soon!
        reactor.callLater(0.1, self.sendMessages)
        
    # Gets the world owner's name (from the world.meta) of a world that isn't currently loaded.
    def getWorldOwnerFromFile(self, world_id):
        config = ConfigParser()
        config.read('worlds/%s/world.meta' % world_id)
        owner = "n/a"
        if config.has_section("owner"):
            owner = config.get("owner", "owner").lower()
        return owner
        
    def addWorldOwnerToIndex(self, world_id, owner_name):
        if len(owner_name) == 0:
            name = "n/a"
        else:
            name = owner_name.lower()
        if name not in self.worldowners:
            self.worldowners[name] = [world_id]
        else:
            self.worldowners[name].append(world_id)     # ideally we shouldn't ever need to check if it's already in there
        
    def removeWorldOwnerFromIndex(self, world_id, owner_name):
        if len(owner_name) == 0:
            name = "n/a"
        else:
            name = owner_name.lower()
        if name in self.worldowners:                            # just in case it somehow isn't there
            self.worldowners[owner_name].remove(world_id)
        
    def updateWorldOwnerIndex(self, world_id, old_owner, new_owner):
        self.removeWorldOwnerFromIndex(world_id, old_owner)
        self.addWorldOwnerToIndex(world_id, new_owner)

    def createWorld(self, world_id, sx, sy, sz):
        grass_to = (sy // 2)
        world = World.create(
            "worlds/%s" % world_id,
            sx, sy, sz, # Size
            sx//2,grass_to+2, sz//2, 0, # Spawn
            ([BLOCK_DIRT]*(grass_to-1) + [BLOCK_GRASS] + [BLOCK_AIR]*(sy-grass_to)) # Levels
            )
        self.addWorldOwnerToIndex(world_id, "n/a")

    def createEmptyWorld(self, world_id, sx, sy, sz):
        grass_to = 2
        world = World.create(
            "worlds/%s" % world_id,
            sx, sy, sz, # Size
            sx//2,grass_to+2, sz//2, 0, # Spawn
            ([BLOCK_GRASS]*(grass_to-1) + [BLOCK_AIR] + [BLOCK_AIR]*(sy-grass_to)) # Levels
            )
        self.addWorldOwnerToIndex(world_id, "n/a")
        
    def newWorld(self, new_name, template="default"):
        "Creates a new world from some template."
        if not os.path.isdir("core/templates/%s/" % template):
            return "That template doesn't exist."
        # Make the directory
        try:
            os.mkdir("worlds/%s" % new_name)
        except:
            return "Sorry, that world already exists!"
        # Find the template files, copy them to the new location
        for filename in ["blocks.gz", "world.meta"]:
            try:
                shutil.copyfile("core/templates/%s/%s" % (template, filename), "worlds/%s/%s" % (new_name, filename))
            except:
                return "That template doesn't exist."
        self.addWorldOwnerToIndex(new_name, "n/a")

    def renameWorld(self, old_worldid, new_worldid):
        "Renames a world."
        assert old_worldid not in self.worlds
        assert self.world_exists(old_worldid)
        assert not self.world_exists(new_worldid)
        os.rename("worlds/%s" % (old_worldid), "worlds/%s" % (new_worldid))
        # Update world-owners index
        owner = self.getWorldOwnerFromFile(new_worldid)
        self.removeWorldOwnerFromIndex(old_worldid, owner)
        self.addWorldOwnerToIndex(new_worldid, owner)
            
    def deleteWorld(self, world_id):
        if not os.path.exists("worlds/%s" % world_id):
            return None
        if world_id in self.worlds:
            self.unloadWorld(world_id)
        owner = self.getWorldOwnerFromFile(world_id)
        delname = world_id
        extra="_0"
        if os.path.exists("worlds/.trash/%s" %(delname)):
            while True:
                if os.path.exists("worlds/.trash/%s" %(delname+extra)):
                    extra = "_" + str(int(extra[1:])+1)
                else:
                    delname = delname+extra
                    break
        shutil.copytree("worlds/%s" % world_id, "worlds/.trash/%s" %(delname))
        shutil.rmtree("worlds/%s" % world_id)
        self.removeWorldOwnerFromIndex(world_id, owner)
        return delname
        
    def undeleteWorld(self, name):
        world_dir = ("worlds/.trash/%s/" % name)
        if not os.path.exists(world_dir):
           return None
        extra="_0"
        if os.path.exists("worlds/%s/" %(name)):
            while True:
                if os.path.exists("worlds/%s/" %(name+extra)):
                    extra = "_" + str(int(extra[1:])+1)
                else:
                    name = name+extra
                    break
        path = ("worlds/%s/" % name)
        shutil.move(world_dir, path)
        # Update world-owners index
        owner = self.getWorldOwnerFromFile(name)
        self.addWorldOwnerToIndex(name, owner)
        return name
    
    # Creates a new world by copying an existing one.
    # Before calling this, you MUST validate that the destination world doesn't already exist, as well as checking that the source world is shut down. See commandWCopy in multiworld.py
    def copyWorld(self, old_worldid, copied_worldid):
        os.mkdir("worlds/%s/" % copied_worldid)
        file1 = open(('worlds/%s/blocks.gz' % old_worldid), 'r' )
        file2 = open(('worlds/%s/world.meta' % old_worldid), 'r' )
        file3 = open(('worlds/%s/blocks.gz' % copied_worldid), 'w' )
        file4 = open(('worlds/%s/world.meta' % copied_worldid), 'w' )
        path = ("worlds/%s/blocks.gz" % copied_worldid)
        path2 = ("worlds/%s/world.meta" % copied_worldid)
        shutil.copy(("worlds/%s/blocks.gz" % old_worldid), path)
        shutil.copy(("worlds/%s/world.meta" % old_worldid), path2)
        # Update world-owners index
        owner = self.getWorldOwnerFromFile(copied_worldid)
        self.addWorldOwnerToIndex(copied_worldid, owner)

    def numberWithPhysics(self):
        "Returns the number of worlds with physics enabled."
        return len([world for world in self.worlds.values() if world.physics])


    # Here are the low-level checks for server-wide ranks. These should only check for the specific rank as per their names.
    # World-ranks are checked via the World object (see world.py)
    
    def isServerOwner(self, username):
        return username.lower() == self.owner

    def isHidden(self, username):
        return username.lower() in self.hidden

    def isDirector(self, username):
        return username.lower() in self.directors

    def isCoder(self, username):
        return username.lower() in self.coders

    def isAdmin(self, username):
        return username.lower() in self.admins

    def isMod(self, username):
        return username.lower() in self.mods

    def isMember(self, username):
        return username.lower() in self.members
        
    # For convenience, the following will check if the user has a certain rank or higher.

    def isHiddenPlus(self, username):
        return self.isHidden(username) or self.isServerOwner(username)    # True for Hidden, ServerOwner

    def isDirectorPlus(self, username):
        return self.isDirector(username) or self.isHiddenPlus(username)   # True for Director, Hidden, ServerOwner

    def isCoderPlus(self, username):
        return self.isCoder(username) or self.isDirectorPlus(username)    # True for Coder, Director, Hidden, ServerOwner

    def isAdminPlus(self, username):
        return self.isAdmin(username) or self.isCoderPlus(username)       # True for Admin, Coder, Director, Hidden, ServerOwner

    def isModPlus(self, username):
        return self.isMod(username) or self.isAdminPlus(username)         # True for Mod, Admin, Coder, Director, Hidden, ServerOwner

    # Staff is just another way of saying Mod+
    def isStaff(self, username):
        return self.isModPlus(username)
    
    # This only tests for the visible staff ranks (Mod, Admin, Coder, Director, ServerOwner).
    def isVisibleStaff(self, username):
        return self.isMod(username) or self.isAdmin(username) or self.isCoder(username) or self.isDirector(username) or self.isServerOwner(username)

    # This is true only when the user has Hidden rank without sharing any other Staff rank.
    def isOnlyHiddenNotVisibleStaff(self, username):
        return self.isHidden(username) and not self.isVisibleStaff(username)

    
    # Here are the low-level checks for server-wide statuses.
        
    def isSilenced(self, username):
        return username.lower() in self.silenced

    def isSpectator(self, username):
        return username.lower() in self.spectators

    def isBanned(self, username):
        return username.lower() in self.banned

    def isIpBanned(self, ip):
        return ip in self.ipbanned

    def addBan(self, username, reason):
        self.banned[username.lower()] = reason

    def removeBan(self, username):
        del self.banned[username.lower()]

    def banReason(self, username):
        return self.banned[username.lower()]

    def addIpBan(self, ip, reason):
        self.ipbanned[ip] = reason

    def removeIpBan(self, ip):
        del self.ipbanned[ip]

    def ipBanReason(self, ip):
        return self.ipbanned[ip]

        
    def addAward(self, award, username):
        # Add an award to a user.
        filep = open("config/data/awards.meta", "a+")
        awardmsg5 = str(award)
        awardmsg4 = awardmsg5.replace("[", "")
        awardmsg3 = awardmsg4.replace("]", "")
        awardmsg2 = awardmsg3.replace(",", "")
        awardmsg = awardmsg2.replace("'", "")
        filep.write(str(username)+" "+awardmsg+"\n")
        filep.close()

    def world_exists(self, world_id):
        "Says if the world exists (even if unbooted)"
        return os.path.isdir("worlds/%s/" % world_id)

    def AutoBackup(self):
        for world in self.worlds:
            self.Backup(world)
        if self.backup_auto:
            reactor.callLater(float(self.backup_freq * 60), self.AutoBackup)

    def Backup(self, world_id):
        world_dir = ("worlds/%s/" % world_id)
        if world_id == self.default_name and not self.backup_default:
            return
        if not os.path.exists(world_dir):
            self.logger.info("World %s does not exist." % (world.id))
        else:
            if not os.path.exists(world_dir+"backup/"):
                os.mkdir(world_dir+"backup/")
            folders = os.listdir(world_dir+"backup/")
            backups = list([])
            for x in folders:
                if x.isdigit():
                    backups.append(x)
            backups.sort(lambda x, y: int(x) - int(y))
            path = os.path.join(world_dir+"backup/", "0")
            if backups:
                path = os.path.join(world_dir+"backup/", str(int(backups[-1])+1))
            os.mkdir(path)
            shutil.copy(world_dir + "blocks.gz", path)
            shutil.copy(world_dir + "world.meta", path)
            try:
                self.logger.info("%s's backup %s is saved." % (world_id, str(int(backups[-1])+1)))
            except:
                self.logger.info("%s's backup 0 is saved." % (world_id))
            if len(backups)+1 > self.backup_max:
                for i in range(0,((len(backups)+1)-self.backup_max)):
                    shutil.rmtree(os.path.join(world_dir+"backup/", str(int(backups[i]))))

    def messagestrip(factory,message):
        strippedmessage = ""
        for x in message:
            if ord(str(x)) < 128:
                strippedmessage = strippedmessage + str(x)
        message = strippedmessage
        for x in factory.filter:
            rep = re.compile(x[0], re.IGNORECASE)
            message = rep.sub(x[1], message)
        return message   
    
    def loadArchives(self):
        self.archives = {}
        for name in os.listdir("core/archives/"):
            if os.path.isdir(os.path.join("core/archives", name)):
                for subfilename in os.listdir(os.path.join("core/archives", name)):
                    match = re.match(r'^(\d\d\d\d\-\d\d\-\d\d_\d?\d\_\d\d)$', subfilename)
                    if match:
                        when = match.groups()[0]
                        try:
                            when = datetime.datetime.strptime(when, "%Y/%m/%d %H:%M:%S")
                        except ValueError, e:
                            self.logger.warning("Bad archive filename %s" % subfilename)
                            continue
                        if name not in self.archives:
                            self.archives[name] = {}
                        self.archives[name][when] = "%s/%s" % (name, subfilename)
        self.logger.info("Loaded %s discrete archives." % len(self.archives))
        reactor.callLater(300, self.loadArchives)

    def announceGlobal(self, actionType, invokerUsername, targetUsername, reason=""):
        if actionType == ACTION_KICK:
            tag = "KICK"
            action = "was kicked"
        elif actionType == ACTION_BAN:
            tag = "BAN"
            action = "was banned"
        elif actionType == ACTION_UNBAN:
            tag = "UNBAN"
            action = "was unbanned"
        elif actionType == ACTION_SILENCE:
            tag = "SILENCE"
            action = "was silenced"
        elif actionType == ACTION_UNSILENCE:
            tag = "UNSILENCE"
            action = "was unsilenced"
        elif actionType == ACTION_IPBAN:
            tag = "IPBAN"
            action = "was IPBanned"
        announcement = "[%s] &6%s %s" % (tag, targetUsername, action)
        if len(invokerUsername) > 0:
            announcement += " by " + invokerUsername
        announcement += "."
        if len(reason) > 0:
            announcement += " Reason: " + reason
        self.queue.put((None, TASK_SERVERURGENTMESSAGE, announcement))
