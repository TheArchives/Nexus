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

import os, shutil
from reqs.twisted.internet import reactor
from core.plugins import ProtocolPlugin
from ConfigParser import RawConfigParser as ConfigParser
from core.decorators import *
from core.constants import *

class BackupPlugin(ProtocolPlugin):

    commands = {
    "backup": "commandBackup",
    "backups": "commandBackups",
    "restore": "commandRestore",
    "viewbackup": "commandViewBackup",
    "vb": "commandViewBackup",
    }

    @world_list
    @op_only
    def commandBackup(self, parts, fromloc, overriderank):
        "/backup worldname - Op\nMakes a backup copy of the world."
        if len(parts) == 1:
            parts.append(self.client.world.basename.lstrip("worlds"))
        world_id = parts[1]
        world_dir = ("worlds/%s/" % world_id)
        if not os.path.exists(world_dir):
           self.client.sendServerMessage("World %s does not exist." % (world_id))
        else:
            if not os.path.exists(world_dir+"backup/"):
                os.mkdir(world_dir+"backup/")
            folders = os.listdir(world_dir+"backup/")
            if len(parts) > 2:
                path = os.path.join(world_dir+"backup/", parts[2])
                if os.path.exists(path):
                    self.client.sendServerMessage("Backup %s already exists. Pick a different name." % parts[2])
                    return
            else:
                backups = list([])
                for x in folders:
                    if x.isdigit():
                        backups.append(x)
                backups.sort(lambda x, y: int(x) - int(y))
                path = os.path.join(world_dir+"backup/", "0")
                if backups:
                    path = os.path.join(world_dir+"backup/", str(int(backups[-1])+1))
            os.mkdir(path)
            try:
                shutil.copy(world_dir + "blocks.gz", path)
                shutil.copy(world_dir + "world.meta", path)
            except:
                self.client.sendServerMessage("Your backup attempt has went wrong, please try again.")
            if len(parts) > 2:
                self.client.sendServerMessage("Backup %s saved." % parts[2])
            else:
                try:
                    self.client.sendServerMessage("Backup %s saved." % str(int(backups[-1])+1))
                except:
                    self.client.sendServerMessage("Backup 0 saved.")

    @world_list
    @op_only
    def commandRestore(self, parts, fromloc, overriderank):
        "/restore worldname number - Op\nRestore world to indicated number."
        if len(parts) < 2:
            self.client.sendServerMessage("Please specify at least a world ID!")
        else:
            world_id = parts[1].lower()
            world_dir = ("worlds/%s/" % world_id)
            if not self.client.isModPlus():
                # ensure user has proper rank in the target world (the check to run this command only counts the world they're currently in)
                canRestore = False
                config = ConfigParser()
                config.read(world_dir+"world.meta") # this still has an issue: it won't pick up recent rank changes that haven't been flushed to the file yet. but it's good enough in geneal.
                if config.has_section("owner"):
                    print config.get("owner", "owner")
                    if config.get("owner", "owner").lower() == self.client.username.lower():
                        canRestore = True
                if config.has_section("ops"):
                    for op in config.options("ops"):
                        print op
                        if op.lower() == self.client.username.lower():
                            canRestore = True
                if not canRestore:
                    self.client.sendServerMessage("You are not allowed to restore that world!")
                    return
            if len(parts) < 3:
                try:
                    backups = os.listdir(world_dir+"backup/")
                except:
                    self.client.sendServerMessage("Syntax: /restore worldname number")
                    return
                backups.sort(lambda x, y: int(x) - int(y))
                backup_number = str(int(backups[-1]))
            else:
                backup_number = parts[2]
            if not os.path.exists(world_dir+"backup/%s/" % backup_number):
                self.client.sendServerMessage("Backup %s does not exist." % backup_number)
            else:                    
                if not os.path.exists(world_dir+"blocks.gz.new"):
                    shutil.copy(world_dir+"backup/%s/blocks.gz" % backup_number, world_dir)
                    try:
                        shutil.copy(world_dir+"backup/%s/world.meta" % backup_number, world_dir)
                        os.remove(world_dir+"blocks.db")    # remove blocktracker data since it's no longer valid
                    except:
                        pass
                else:
                    reactor.callLater(1, self.commandRestore(self, parts, fromloc, overriderank))
                default_name = self.client.factory.default_name
                self.client.factory.unloadWorld("worlds/%s" % world_id, world_id)
                self.client.sendServerMessage("%s has been restored to %s and booted." % (world_id, backup_number))
                if world_id in self.client.factory.worlds:
                    for client in self.client.factory.worlds[world_id].clients:
                        client.changeToWorld(world_id)

    @world_list
    def commandBackups(self, parts, fromloc, overriderank):
        "/backups - Guest\nLists all backups this world has."
        try:
            world_dir = ("worlds/%s/" % self.client.world.id)
            folders = os.listdir(world_dir+"backup/")
            Num_backups = list([])
            Name_backups = list([])
            for x in folders:
                if x.isdigit():
                    Num_backups.append(x)
                else:
                    Name_backups.append(x)
            Num_backups.sort(lambda x, y: int(x) - int(y))
            if Num_backups > 2:
                self.client.sendServerList(["Backups for %s:" % self.client.world.id] + [Num_backups[0] + "-" + Num_backups[-1]] + Name_backups)
            else:
                self.client.sendServerList(["Backups for %s:" % self.client.world.id] + Num_backups + Name_backups)
        except:
            self.client.sendServerMessage("Sorry, but there are no backups for %s." % self.client.world.id)

    @world_list
    @only_string_command("world name")
    def commandViewBackup(self, world_id, byuser, overriderank, params=None):
        "/viewbackup worldname backup - Guest\nMoves you into worldname's backup"
        world_id = world_id.replace(" ", "/backup/")
        if world_id not in self.client.factory.worlds:
            self.client.sendServerMessage("Attempting to boot and join '%s'" % world_id)
            try:
                self.client.factory.loadWorld("worlds/%s" % world_id, world_id)
            except AssertionError:
                self.client.sendServerMessage("There is no backup by that name.")
                return
        self.client.changeToWorld(world_id)
