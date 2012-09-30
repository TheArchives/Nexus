# The Nexus software is licensed under the BSD 2-Clause license.
#
# You should have recieved a copy of this license with the software.
# If you did not, you can find one at the following link.
#
# http://opensource.org/licenses/bsd-license.php
# http://opensource.org/licenses/bsd-license.php
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

import os, sys, math, traceback, logging
from core.plugins import ProtocolPlugin
from core.decorators import *
from core.constants import *
from reqs.twisted.internet import reactor
from random import randint
from time import time

initfile = open("core/entities/__init__.py")
exec initfile
initfile.close()
initfile = None
entitycodedict = {}
entityselectdict = {}
entitycreatedict = {}
validentities = []
maxentitiesperworld = 40
#maxentitiesperworld = self.factory.elimit

def loadentities():
    global validentities
    datafilelist = os.listdir("core/entities/")
    del datafilelist[datafilelist.index("__init__.py")]
    listofentityfiles = []
    for entry in datafilelist:
        if entry.find('_') == -1 and entry.endswith('.py'):
            listofentityfiles.append(entry)
    for entry in listofentityfiles:
        entitycodedict[entry[:-3]] = open("core/entities/%s" % entry)
    validentities = entitycodedict.keys()
    for entry in validentities:
        possibeAliasFile = entry + "_aliases.txt"
        if possibeAliasFile in datafilelist:
            for alias in open("core/entities/%s" % possibeAliasFile):
                alias = alias.rstrip()
                if alias != '':
                    entitycodedict[alias] = entitycodedict[entry]
    validentities = []
    for entityname in entitycodedict:
        if entityname not in unselectableentities:
            validentities.append(entityname)
    for entry in validentities:
        possibeSelectFile = entry + "_select.py"
        if possibeSelectFile in datafilelist:
            entityselectdict[entry] = open("core/entities/%s" % possibeSelectFile)

        possibeCreateFile = entry + "_create.py"
        if possibeCreateFile in datafilelist:
            entitycreatedict[entry] = open("core/entities/%s" % possibeCreateFile)
loadentities()
for validentity in validentities:
    if validentity not in entityblocklist:
        entityblocklist[validentity] = [(0,0,0)]

class EntityPlugin(ProtocolPlugin):

    commands = {
        "entity": "commandEntity",
        "entityclear": "commandEntityclear",
        "numentities": "commandNumentities",
        "entities": "commandEntities",
        "mob": "commandEntity",
        "mobclear": "commandEntityclear",
        "nummobs": "commandNumentities",
        "mobs": "commandEntities",
        "item": "commandEntity",
        "itemclear": "commandEntityclear",
        "numitems": "commandNumentities",
        "items": "commandEntities",
    }

    hooks = {
        "blockchange": "blockChanged",
        "poschange": "posChanged",
        "newworld": "newWorld",
    }

    def gotClient(self):
        self.var_entityselected = "None"
        self.var_entityparts = []

    def newWorld(self, world):
        "Hook to reset entity making in new worlds."
        self.var_entityselected = "None"

    def blockChanged(self, x, y, z, block, selected_block, fromloc):
        "Hook trigger for block changes."
        if fromloc != "user":
            # People shouldn't be blbing mobs
            return
        world = self.client.world
        try:
            px, py, pz, ph, pp = self.client.x>>5, self.client.y>>5, self.client.z>>5, self.client.h, self.client.p
        except:
            pass
        world.entities_worldblockchangesdict[self.client] = ((x, y, z, time(), selected_block, block), (px, py, pz, ph, pp))
        entitylist = world.entitylist
        dellist = []
        for index in range(len(entitylist)):
            entity = entitylist[index]
            identity = entity[0]
            i, j, k = entity[1]
            if (i, j, k) == (x, y, z) or (identity in twoblockhighentities and (i, j+1 ,k) == (x, y, z)):
                dellist.append(index)
        dellist.reverse()
        for index in dellist:
            del entitylist[index]
            self.client.sendServerMessage("The entity is now deleted.")
        if block != 0:
            if self.var_entityselected != "None":
                if len(entitylist) >= maxentitiesperworld:
                    self.client.sendServerMessage("Max entities per world exceeded.")
                    return
                if self.var_entityselected in entitycreatedict:
                    exec entitycreatedict[self.var_entityselected]
                    entitycreatedict[self.var_entityselected].seek(0)
                else:
                    entitylist.append([self.var_entityselected, (x, y, z), 8, 8])
                    self.client.sendServerMessage("The entity was created.")

    def posChanged(self, x, y, z, h, p):
        username = self.client.username
        world = self.client.world
        if not world.entitylist:
            return  # don't bother doing any more processing if there aren't any entities in that world
        # determine which user should be the keyuser - the only one in the world that provokes processing of the entity logic
        try:
            keyuser = world.var_entities_keyuser
        except:
            world.var_entities_keyuser = username
            keyuser = username
        clients = world.clients
        worldusernamelist = []
        for client in clients:
            worldusernamelist.append(client.username)
        if not keyuser in worldusernamelist:
            world.var_entities_keyuser = username
            keyuser = username
        if username == keyuser:
            # process logic for all entities in the world
            entitylist = world.entitylist
            worldblockchangesdict = world.entities_worldblockchangesdict
            entities_childerenlist = world.entities_childerenlist
            worldblockchangedellist = []
            var_dellist = []
            var_abstime = time()
            userpositionlist = []
            for user in clients:
                if user is not None:
                    userpositionlist.append((user,(user.x >> 5,user.y >> 5,user.z >> 5)))
            var_num = len(entitylist)
            if var_num > maxentitiystepsatonetime:
                var_num = maxentitiystepsatonetime
            for index in range(var_num):
                entity = entitylist[index]
                var_type = entity[0]
                var_position = entity[1]
                entity[2] -= 1
                if entity[2] < 0:
                    try:
                        entity[2] = entity[3]
                        x,y,z = var_position
                        if not (0 <= x < world.x and 0 <= y < world.y and 0 <= z < world.z):
                            var_dellist.append(index)
                            if var_type in var_childrenentities:
                                del entities_childerenlist[entities_childerenlist.index(entity[5])]
                        elif (var_type in twoblockhighentities or var_type == "spawner" or var_type in twoblockhighshootingentities) and not (0 <= x < world.x and 0 <= y+1 < world.y and 0 <= z < world.z):
                            var_dellist.append(index)
                        elif var_type == "cannon":
                            # these variables also used later
                            var_orientation = entity[5]
                            x,y,z = var_position
                            if var_orientation == 0:
                                var_sensorblocksoffsets = ((0,1,-2),(0,2,-2))
                                var_loadblockoffset = (0,0,-1)
                            elif var_orientation == 1:
                                var_sensorblocksoffsets = ((2,1,0),(2,2,0))
                                var_loadblockoffset = (1,0,0)
                            elif var_orientation == 2:
                                var_sensorblocksoffsets = ((0,1,2),(0,2,2))
                                var_loadblockoffset = (0,0,1)
                            elif var_orientation == 3:
                                var_sensorblocksoffsets = ((-2,1,0),(-2,2,0))
                                var_loadblockoffset = (-1,0,0)
                            n,m,o = var_loadblockoffset
                            if not (0 <= x+n < world.x and 0 <= y+m < world.y and 0 <= z+o < world.z):
                                var_dellist.append(index)
                            else:
                                for q,r,s in var_sensorblocksoffsets:
                                    if not (0 <= x+q < world.x and 0 <= y+r < world.y and 0 <= z+s < world.z):
                                        var_dellist.append(index)
                        if index not in var_dellist:
                            if var_type in entitycodedict:
                                exec entitycodedict[var_type]
                                entitycodedict[var_type].seek(0)
                            else:
                                self.client.sendWorldMessage("UNKOWN ENTITY IN WORLD - FIX THIS!")
                    except:
                        self.client.sendPlainWorldMessage(traceback.format_exc().replace("Traceback (most recent call last):", ""))
                        self.client.sendPlainWorldMessage("Internal Server Error - Traceback (Please report this to the Server Staff or the iCraft Team, see /about for contact info)")
                        self.client.logger.error(traceback.format_exc())
                        world.entitylist = []
                        return
                entity[1] = var_position
            var_dellist2 = []
            for index in var_dellist:
                if index not in var_dellist2:
                        var_dellist2.append(index)
            var_dellist2.sort()
            var_dellist2.reverse()
            for index in var_dellist2:
                del entitylist[index]
            worldblockchangedellist2 = []
            for index in worldblockchangedellist:
                if index not in worldblockchangedellist2:
                        worldblockchangedellist2.append(index)
            for index in worldblockchangedellist2:
                del worldblockchangesdict[index]
            if len(entitylist) > maxentitiystepsatonetime:
                for i in range(maxentitiystepsatonetime):
                    entitylist.append(entitylist.pop(0))

    @op_only
    def commandEntity(self, parts, fromloc, overriderank):
        "/entity entityname - Op\nAliases: item, mob\nCreates the specified entity."
        if len(parts) < 2:
            if self.var_entityselected == "None":
                self.client.sendServerMessage("Please enter an entity name (type /entities for a list)")
            else:
                self.var_entityselected = "None"
                self.client.sendServerMessage("The entity has been deselected.")
        else:
            world = self.client.world
            entity = parts[1]
            var_continue = True
            if entity in validentities:
                if entity in entityselectdict:
                    exec entityselectdict[entity]
                    entityselectdict[entity].seek(0)
                else:
                    self.var_entityselected = entity
            else:
                self.client.sendServerMessage("%s is not a valid entity." % entity)
                return
            if var_continue:
                self.client.sendServerMessage("The entity %s has been selected." % entity)
                self.client.sendServerMessage("To deselect just type /entity")

    @op_only
    def commandNumentities(self, parts, fromloc, overriderank):
        "/numentities - Op\nAliases: numitems, nummobs\nTells you the number of entities in the world."
        world = self.client.world
        entitylist = world.entitylist
        self.client.sendServerMessage(str(len(entitylist)))

    @op_only
    def commandEntityclear(self, parts, fromloc, overriderank):
        "/entityclear - Op\nAliases: itemclear, mobclear\nClears the entities from the world."
        world = self.client.world
        for entity in self.client.world.entitylist:
            var_id = entity[0]
            x,y,z = entity[1]
            if var_id in entityblocklist:
                for offset in entityblocklist[var_id]:
                    ox,oy,oz = offset
                    rx,ry,rz = x+ox,y+oy,z+oz
                    block = '\x00'
                    world[rx, ry, rz] = block
                    self.client.queueTask(TASK_BLOCKSET, (rx, ry, rz, block), world=world)
                    self.client.sendBlock(rx, ry, rz, block)
            elif var_id == "cannon":
                var_orientation = entity[5]
                if var_orientation == 0:
                    var_sensorblocksoffsets = ((0,1,-2),(0,2,-2))
                    var_loadblockoffset = (0,0,-1)
                elif var_orientation == 1:
                    var_sensorblocksoffsets = ((2,1,0),(2,2,0))
                    var_loadblockoffset = (1,0,0)
                elif var_orientation == 2:
                    var_sensorblocksoffsets = ((0,1,2),(0,2,2))
                    var_loadblockoffset = (0,0,1)
                elif var_orientation == 3:
                    var_sensorblocksoffsets = ((-2,1,0),(-2,2,0))
                    var_loadblockoffset = (-1,0,0)
                block = '\x00'
                world[x, y, z] = block
                self.client.queueTask(TASK_BLOCKSET, (x, y, z, block), world=world)
                self.client.sendBlock(x, y, z, block)
                i,j,k = var_loadblockoffset
                rx,ry,rz = x+i,y+j,z+k
                world[rx, ry, rz] = block
                self.client.queueTask(TASK_BLOCKSET, (rx, ry, rz, block), world=world)
                self.client.sendBlock(rx, ry, rz, block)
                for i,j,k in var_sensorblocksoffsets:
                    rx,ry,rz = x+i,y+j,z+k
                    world[rx, ry, rz] = block
                    self.client.queueTask(TASK_BLOCKSET, (rx, ry, rz, block), world=world)
                    self.client.sendBlock(rx, ry, rz, block)
            else:
                self.client.sendServerMessage("Entity not registered in the entityblocklist.")
        self.client.world.entitylist = []
        self.client.sendWorldMessage("The entities have been cleared.")

    @op_only
    def commandEntities(self, parts, fromloc, overriderank):
        "/entities - Op\nAliases: items, mobs\nDisplays available entities."
        varsorted_validentities = validentities[:]
        varsorted_validentities.sort()
        self.client.sendServerList(["Available entities:"] + varsorted_validentities)
