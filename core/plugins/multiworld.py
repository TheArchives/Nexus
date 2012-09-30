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

import random, os, shutil, math
from ConfigParser import RawConfigParser as ConfigParser
from core.plugins import ProtocolPlugin
from core.decorators import *
from core.constants import *
from core.world import World

class MultiWorldPlugin(ProtocolPlugin):
    
    commands = {
        "new": "commandNew",
        "mapadd": "commandNew",
        "rename": "commandRename",
        "maprename": "commandRename",
        "shutdown": "commandShutdown",
        "sd": "commandShutdown",
        "worldsp": "commandOwnedWorlds",
        "ownedworlds": "commandOwnedWorlds",
        "ow": "commandOwnedWorlds",
        "l": "commandLoad",
        "j": "commandLoad",
        "load": "commandLoad",
        "join": "commandLoad",
        "map": "commandLoad",
        "boot": "commandBoot",
        "worlddump": "commandWorldDump",
        "worlds": "commandWorlds",
        "maps": "commandWorlds",
        "worldsearch": "commandWorldSearch",
        "templates": "commandTemplates",
        "reboot": "commandReboot",
        "reload": "commandReboot",
        "home": "commandHome",
        "create": "commandCreate",
        "delete": "commandDelete",
        "mapdelete": "commandDelete",
        "deletebackup": "commandDeleteBackup",
        "db": "commandDeleteBackup",
        "delbu": "commandDeleteBackup",
        "cw": "commandWCopy",
        "undelete": "commandUnDelete",
        "deleted": "commandDeleted",
        "rejoin": "commandReJoin",
        "createempty": "commandCreateEmpty",
    }

    def commandReJoin(self, parts, fromloc, overriderank):
        "/rejoin - Guest\nRejoins your current world."
        if len(parts) > 1:
            self.client.sendServerMessage("This command doesn't require parameters.")
        else:
            world_id = self.client.world.id
            self.client.changeToWorld(world_id)
            
    @world_list
    def commandOwnedWorlds(self, parts, fromloc, overriderank):
        "/ownedworlds [playername] - Guest\nAliases: ow, worldsp\nLists worlds owned by a player."
        if len(parts) >= 2:
            name = parts[1].lower()
        else:
            name = self.client.username.lower()
        worldlist = []
        if name in self.client.factory.worldowners:
            worldlist = list(self.client.factory.worldowners[name])
        worldlist.sort()
        worldlist.insert(0, ("Worlds owned by %s:" % name))
        self.client.sendServerList(worldlist)
    
    @world_list
    @admin_only
    def commandNew(self, parts, fromloc, overriderank):
        "/new worldname templatename - Admin\nAliases: mapadd\nMakes a new world, and boots it."
        if len(parts) == 1:
            self.client.sendServerMessage("Please specify a new worldname.")
        elif self.client.factory.world_exists(parts[1]):
            self.client.sendErrorMessage("World name in use.")
        else:
            if len(parts) == 2:
                self.client.sendServerMessage("Please specify a template.")
                return
            elif len(parts) == 3 or len(parts) == 4:
                template = parts[2]
            else:
                self.client.sendServerMessage("Please specify a template.")
                return
            world_id = parts[1].lower()
            result = self.client.factory.newWorld(world_id, template)
            if result is not None:
                self.client.sendServerMessage(result)
            else:
                self.client.factory.loadWorld("worlds/%s" % world_id, world_id)
                self.client.factory.worlds[world_id].all_write = False
                if len(parts) < 4:
                    self.client.sendServerMessage("World '%s' made and booted." % world_id)

    @world_list
    @mod_only
    def commandRename(self, parts, fromloc, overriderank):
        "/rename worldname newworldname - Mod\nAliases: maprename\nRenames a SHUT DOWN world."
        if len(parts) < 3:
            self.client.sendServerMessage("Please specify two worldnames.")
        else:
            old_worldid = parts[1].lower()
            new_worldid = parts[2].lower()
            if old_worldid in self.client.factory.worlds:
                self.client.sendErrorMessage("World '%s' is booted, please shut it down!" % old_worldid)
            elif not self.client.factory.world_exists(old_worldid):
                self.client.sendErrorMessage("There is no world '%s'." % old_worldid)
            elif self.client.factory.world_exists(new_worldid):
                self.client.sendErrorMessage("There is already a world called '%s'." % new_worldid)
            else:
                self.client.factory.renameWorld(old_worldid, new_worldid)
                self.client.sendServerMessage("World '%s' renamed to '%s'." % (old_worldid, new_worldid))
    
    @world_list
    @mod_only
    def commandShutdown(self, parts, byuser, overriderank):
        "/shutdown worldname - Mod\nTurns off the named world."
        if len(parts) == 1:
            world = self.client.world.id
        else:
            if self.client.isModPlus():
                world = parts[1]
            else:
                self.client.sendServerMessage("You don't have the proper rank to do this.")
        if world in self.client.factory.worlds:
            self.client.factory.unloadWorld(world)
            self.client.sendServerMessage("World '%s' unloaded." % world)
        else:
            self.client.sendErrorMessage("World '%s' isn't booted." % world)

    @world_list
    @mod_only
    def commandReboot(self, parts, fromloc, overriderank):
        "/reboot worldname - Mod\nAliases: reload\nReboots a world"
        if len(parts) == 1:
            self.client.sendServerMessage("Please specify a worldname.")
        else:
            if parts[1] in self.client.factory.worlds:
                self.client.factory.rebootWorld(parts[1])
                self.client.sendServerMessage("World %s rebooted" % parts[1])
            else:
                self.client.sendErrorMessage("World '%s' isnt booted." % parts[1])

    @world_list
    def commandBoot(self, parts, fromloc, overriderank):
        "/boot worldname - Guest\nStarts up a new world."
        if len(parts) == 1:
            self.client.sendServerMessage("Please specify a worldname.")
        else:
            if parts[1] in self.client.factory.worlds:
                self.client.sendServerMessage("World '%s' already exists!" % parts[1])
            else:
                try:
                    self.client.factory.loadWorld("worlds/%s" % parts[1], parts[1])
                    self.client.sendServerMessage("World '%s' booted." % parts[1])
                except AssertionError:
                    self.client.sendErrorMessage("There is no world by that name.")
    
    @world_list
    @only_string_command("world name")
    def commandLoad(self, world_id, fromloc, overriderank, params=None):
        "/l worldname [backup] - Guest\nAliases: j, join, load, map\nMoves you into world 'worldname'"
        world_id = world_id.replace("/", "/backup/")
        if world_id not in self.client.factory.worlds:
            self.client.sendServerMessage("Attempting to boot and join '%s'" % world_id)
            try:
                self.client.factory.loadWorld("worlds/%s" % world_id, world_id)
            except AssertionError:
                self.client.sendErrorMessage("There is no world by that name.")
                return
        world = self.client.factory.worlds[world_id]
        if (self.client.canEnter(world)):
            self.client.changeToWorld(world_id)
        else:
            self.client.sendServerMessage(self.client.getReasonCannotEnter(world))
    
    #@world_list
    def commandWorldDump(self, parts, fromloc, overriderank):
        "/worlddump [letter|all] - Guest\nLists available worlds - by letter, online, or all."
        if len(parts) != 2 and len(parts) != 3:
            self.client.sendServerMessage("Do /worlds all for all worlds or choose a letter.")
            self.client.sendServerList(["Online:"] + [id for id, world in self.client.factory.worlds.items() if self.client.canEnter(world)])
            return
        else:
            worldlist = os.listdir("worlds/")
            newworldlist = []
            for world in worldlist:
                if not world.startswith("."):
                    newworldlist.append(world)
            if parts[1] == 'all':
                if len(newworldlist) > 100:
                    self.client.sendServerMessage("There are too many worlds to list them all.")
                else:
                    self.client.sendServerList(["Worlds:"] + newworldlist)
                return
            if len(parts[1]) != 1:
                self.client.sendServerMessage("Only specify one starting letter per entry, not multiple")
                return
            if len(parts)==3:
                if len(parts[2]) != 1:
                    self.client.sendServerMessage("Only specify one starting letter per entry, not multiple")
                    return
            letter1 = ord(parts[1].lower())
            if len(parts)==3:
                letter2 = ord(parts[2].lower())
            else:
                letter2 = letter1
            if letter1>letter2:
                a = letter1
                letter1 = letter2
                letter2 = a
            newlist = []
            for world in newworldlist:
                if letter1 <= ord(world[0]) <= letter2:
                    newlist.append(world)
            self.client.sendServerList(["Worlds:"] + newlist)
            
    @world_list
    def commandWorlds(self, parts, fromloc, overriderank):
        "/worlds [text] [page] - Guest\nAliases: maps\nLists worlds starting with 'text'."
        if len(parts) != 2 and len(parts) != 3:
            #self.client.sendServerMessage("Do /worlds all for all worlds or choose a letter.")
            self.client.sendServerList(["Online:"] + [id for id, world in self.client.factory.worlds.items() if self.client.canEnter(world)])
            return
        else:
            if len(parts)==3:
                try:
                    page = int(parts[2])
                except ValueError:
                    self.client.sendServerMessage("Page must be a Number.")
                    return
            else:
                page = 1
            worldlist = os.listdir("worlds/")
            resultlist = []
            matchcount = 0
            numperpage = 50
            for world in worldlist:
                if world.startswith(parts[1]) and not world.startswith("."):
                    matchcount += 1
                    if matchcount > numperpage * (page-1) and len(resultlist) < numperpage:
                        resultlist.append(world)
            self.client.sendServerList(["Worlds:"] + resultlist)
            self.client.sendServerMessage("Page %s of %s" % ( page, int(math.ceil(matchcount/float(numperpage))) ))
            
    @world_list
    def commandWorldSearch(self, parts, fromloc, overriderank):
        "/worldsearch searchtext [page] - Guest\nLists worlds that contain the search text."
        if len(parts) < 2:
            self.client.sendServerMessage("You must enter search text.")
        elif len(parts[1]) < 3:
            self.client.sendServerMessage("Search text must be 3 or more characters.")
        else:
            if len(parts)==3:
                try:
                    page = int(parts[2])
                except ValueError:
                    self.client.sendServerMessage("Page must be a Number.")
                    return
            else:
                page = 1
            worldlist = os.listdir("worlds/")
            resultlist = []
            matchcount = 0
            numperpage = 50
            for world in worldlist:
                if world.find(parts[1]) > -1 and not world.startswith("."):
                    matchcount += 1
                    if matchcount > numperpage * (page-1) and len(resultlist) < numperpage:
                        resultlist.append(world)
            self.client.sendServerList(["Worlds:"] + resultlist)
            self.client.sendServerMessage("Page %s of %s" % ( page, int(math.ceil(matchcount/float(numperpage))) ))

    @world_list
    def commandTemplates(self, parts, fromloc, overriderank):
        "/templates - Guest\nLists available templates"
        self.client.sendServerList(["Templates:"] + os.listdir("core/templates/"))

    def commandHome(self, parts, fromloc, overriderank):
        "/home - Guest\nTakes you home, where else?"
        self.client.changeToWorld("default")

    @world_list
    @admin_only
    def commandCreate(self, parts, fromloc, overriderank):
        "/create worldname width height length - Admin\nCreates a new world with specified dimensions."
        if len(parts) == 1:
            self.client.sendServerMessage("Please specify a world name.")
        elif self.client.factory.world_exists(parts[1]):
            self.client.sendServerMessage("World name in use.")
        elif len(parts) < 5:
            self.client.sendServerMessage("Please specify dimensions. (width, length, height)")
        elif int(parts[2]) < 16 or int(parts[3]) < 16 or int(parts[4]) < 16:
            self.client.sendServerMessage("No dimension may be smaller than 16.")
        elif int(parts[2]) > 1024 or int(parts[3]) > 1024 or int(parts[4]) > 1024:
            self.client.sendServerMessage("No dimension may be greater than 1024.")
        elif (int(parts[2]) % 16) > 0 or (int(parts[3]) % 16) > 0 or (int(parts[4]) % 16) > 0:
            self.client.sendServerMessage("All dimensions must be divisible by 16.")
        else:
            world_id = parts[1].lower()
            self.client.factory.createWorld(world_id, int(parts[2]), int(parts[3]), int(parts[4]))
            self.client.factory.loadWorld("worlds/%s" % world_id, world_id)
            self.client.factory.worlds[world_id].all_write = False
            self.client.sendServerMessage("World '%s' made and booted." % world_id)

    @world_list
    @admin_only
    def commandCreateEmpty(self, parts, fromloc, overriderank):
        "/createempty worldname width height length - Admin\nCreates a new world with specified dimensions, hollowed out."
        if len(parts) == 1:
            self.client.sendServerMessage("Please specify a world name.")
        elif self.client.factory.world_exists(parts[1]):
            self.client.sendServerMessage("World name in use.")
        elif len(parts) < 5:
            self.client.sendServerMessage("Please specify dimensions. (width, length, height)")
        elif int(parts[2]) < 16 or int(parts[3]) < 16 or int(parts[4]) < 16:
            self.client.sendServerMessage("No dimension may be smaller than 16.")
        elif int(parts[2]) > 1024 or int(parts[3]) > 1024 or int(parts[4]) > 1024:
            self.client.sendServerMessage("No dimension may be greater than 1024.")
        elif (int(parts[2]) % 16) > 0 or (int(parts[3]) % 16) > 0 or (int(parts[4]) % 16) > 0:
            self.client.sendServerMessage("All dimensions must be divisible by 16.")
        else:
            world_id = parts[1].lower()
            self.client.factory.createEmptyWorld(world_id, int(parts[2]), int(parts[3]), int(parts[4]))
            self.client.factory.loadWorld("worlds/%s" % world_id, world_id)
            self.client.factory.worlds[world_id].all_write = False
            self.client.sendServerMessage("World '%s' made and booted." % world_id)
    
    @world_list
    @admin_only
    def commandDelete(self, parts, fromloc, overriderank):
        "/delete worldname - Admin\nAliases: mapdelete\nSets the specified world to 'ignored'."
        if len(parts) == 1:
            self.client.sendServerMessage("Please specify a worldname.")
        else:
            world_id = parts[1]
            delname = self.client.factory.deleteWorld(world_id)
            if delname == None:
                self.client.sendServerMessage("World %s doesnt exist." %(world_id))
            else:
                self.client.sendServerMessage("World deleted as %s." %(delname))

    @world_list
    @admin_only
    def commandDeleteBackup(self, parts, fromloc, overriderank):
        "/deletebackup worldname backupnum/name - Admin\nAliases: delbu, db\nSets the specified backup to 'ignored'."
        if len(parts) == 1:
            self.client.sendServerMessage("Please specify a worldname.")
        else:
            if not os.path.exists("worlds/%s/backup/%s" % (parts[1], parts[2])):
                self.client.sendErrorMessage("Backup %s/backup/%s doesnt exist." % (parts[1], parts[2]))
                return
            #if parts[1] in self.client.factory.worlds:
                #self.client.factory.unloadWorld(parts[1])#+"/backup/"+parts[2])
            name = parts[1]
            extra="_0"
            if os.path.exists("worlds/.trash/%s" %(name)):
                while True:
                    if os.path.exists("worlds/.trash/%s" %(name+extra)):
                        extra = "_" + str(int(extra[1:])+1)
                    else:
                        name = name+extra
                        break
            shutil.copytree("worlds/%s/backup/%s" % (parts[1], parts[2]) , "worlds/.trash/%s/%s" %(name, parts[2]))
            shutil.rmtree("worlds/%s/backup/%s" % (parts[1], parts[2]))
            self.client.sendServerMessage("Backup deleted as %s." %(name))

    @world_list
    @admin_only
    def commandWCopy(self, parts, fromloc, overriderank):
        "/copyworld worldname newworldname - Mod\nAliases: cw\nCopies a SHUT DOWN world."
        if len(parts) < 3:
            self.client.sendServerMessage("Please specify two worldnames.")
        else:
            old_worldid = parts[1].lower()
            copied_worldid = parts[2].lower()
            if old_worldid in self.client.factory.worlds:
                self.client.sendErrorMessage("World '%s' is booted, please shut it down!" % old_worldid)
            elif not self.client.factory.world_exists(old_worldid):
                self.client.sendErrorMessage("There is no world '%s'." % old_worldid)
            elif self.client.factory.world_exists(copied_worldid):
                self.client.sendErrorMessage("There is already a world called '%s'." % copied_worldid)
            else:
                self.client.factory.copyWorld(old_worldid, copied_worldid)
                self.client.sendServerMessage("World '%s' copied to '%s'." % (old_worldid, copied_worldid))
    
    @world_list
    @admin_only
    def commandUnDelete(self, parts, fromloc, overriderank):
        "/undelete worldname - Admin\nRestores a deleted world."
        if len(parts) < 2:
            self.client.sendServerMessage("Please specify a worldname.")
            return
        name = parts[1].lower()
        restoredname = self.client.factory.undeleteWorld(name)
        if restoredname == None:
            self.client.sendServerMessage("World %s is not in the world trash bin." % name)
        else:
            self.client.sendServerMessage("World restored as %s." % restoredname)

    @world_list
    @admin_only
    def commandDeleted(self, parts, fromloc, overriderank):
        "/deleted [letter] - Admin\nLists deleted worlds - by letter or all."
        if len(parts) != 2 and len(parts) != 3:
            self.client.sendServerMessage("Do '/deleted letter' for all starting with a letter.")
            self.client.sendServerList(["Deleted:"] + os.listdir("worlds/.trash/"))
            return
        else:
            if len(parts[1]) != 1:
                self.client.sendServerMessage("Only specify one starting letter per entry, not multiple")
                return
            if len(parts)==3:
                if len(parts[2]) != 1:
                    self.client.sendServerMessage("Only specify one starting letter per entry, not multiple")
                    return
            letter1 = ord(parts[1].lower())
            if len(parts)==3:
                letter2 = ord(parts[2].lower())
            else:
                letter2 = letter1
            if letter1>letter2:
                a = letter1
                letter1 = letter2
                letter2 = a
            worldlist = os.listdir("worlds/.trash/")
            newlist = []
            for world in worldlist:
                if letter1 <= ord(world[0]) <= letter2 and not world.startswith("."):
                    newlist.append(world)
            self.client.sendServerList(["Deleted:"] + newlist)
