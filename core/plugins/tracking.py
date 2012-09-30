#    iCraft is Copyright 2010 both
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

import traceback
from core.plugins import ProtocolPlugin
from core.decorators import *
from core.constants import *
from reqs.twisted.internet import reactor
from time import time
day = 86400
hour = 3600
min = 60

class Tracking(ProtocolPlugin):

    commands = {
        #"multiundo": "commandMultiUndo",
        #"mode": "commandMode",
        "block": "commandBlock",
        "ungrief": "commandUnGrief",
        "force": "commandForce",
        "undozone": "commandUndoZone",
    }

    hooks = {
        "blockchange": "blockChanged",
        "chatmsg": "chat"
    }

    def gotClient(self):
        self.tracktype = "normal"
        self.question = ""
        self.marker = []

    #def modechange(self, parts, fromloc, overriderank):
    #    if parts[1].lower == "true":
    #        self.trackoff = True
    #    else:
    #        self.trackoff = False

    def blockChanged(self, x, y, z, block, selected_block, fromloc):
        if self.tracktype == "normal":
            "Hook trigger for block changes."
            world = self.client.world
            blockoffset = world.blockstore.get_offset(x, y, z)
            before = ord(world.blockstore.raw_blocks[blockoffset])
            after = (block)
            date = time()
            name = self.client.username
            #print blockoffset, name, date, before, after
            self.client.world.BlockEngine.writetable(blockoffset, before, after, name, date)
        elif self.tracktype == "ungrief":
            try:
                temp = self.client.world.blockstore.get_offset(x,y,z) # (offset, player, date, before, after)
                #print temp
                self.marker = self.client.world.BlockEngine.readd(temp,"id") # format :(124768,     3,     0,  'goober', 1289008346.276)
                #print self.marker
                #self.marker = self.marker[0]
                #print self.marker
                if not self.marker == []:
                    self.question = "Do you want to undo all work by %s?"%str(self.marker[3])
                    self.client.sendServerMessage(self.question)
                    return False
                else:
                    self.client.sendServerMessage("There is no data for this block.")
                    return False
            except:
                self.client.sendServerMessage("Internal Server Error")
                print traceback.format_exc()
        elif self.tracktype == "undo_zone":
            if len(self.marker) == 0:
                #self.marker.append([x,y,z])
                self.marker = [(x,y,z)]
                return False
            elif len(self.marker) == 1:
                self.marker = self.marker[:1] + [(x,y,z)]
                #print "here"
                self.highlight(self.marker[0][0],self.marker[0][1],self.marker[0][2],x, y, z)
                return False
            else:
                self.dehighlight(self.marker[0][0],self.marker[0][1],self.marker[0][2],self.marker[1][0],self.marker[1][1],self.marker[1][2])
                self.marker = self.marker[1:] + [(x,y,z)]
                self.highlight(self.marker[0][0],self.marker[0][1],self.marker[0][2],x, y, z)
                return False
        else:
            pass

    def commandBlock(self, parts, fromloc, overriderank):
        x, y, z = self.client.last_block_changes[0]
        temp = self.client.world.blockstore.get_offset(x,y,z)
        #print self.client.world.BlockEngine.readoffset(temp)
        #print self.client.world.BlockEngine.masterlist

    def commandForce(self, parts, fromloc, overriderank):
        self.client.world.BlockEngine.dbwrite()
        
    def commandUndoZone(self, parts, fromloc, overriderank):
        if len(parts) == 2:
            if parts[1] == "on":
                self.marker = []
                self.tracktype = "undo_zone"
                self.client.sendServerMessage("Undo zone is on. Place/delete a block to highlight it.")
            elif parts[1] == "off":
                self.tracktype = "normal"
                self.question = ""
                if len(self.marker) == 2:
                    self.dehighlight(self.marker[0][0],self.marker[0][1],self.marker[0][2],self.marker[1][0],self.marker[1][1],self.marker[1][2])
                self.marker = []
                self.client.sendServerMessage("Undo zone is off.")
        else:
            self.client.sendServerMessage("You need to specify 'on' or 'off'.")
        #try:
        #    x, y, z = self.client.last_block_changes[0]
        #    x2, y2, z2 = self.client.last_block_changes[1]
        #except IndexError:
        #    self.client.sendServerMessage("You have not clicked two corners yet.")
        #    return
        #if x > x2:
        #    x, x2 = x2, x
        #if y > y2:
        #    y, y2 = y2, y
        #if z > z2:
        #    z, z2 = z2, z
        
    def commandUnGrief(self, parts, fromloc, overriderank):
        if len(parts) == 2:
            if parts[1] == "on":
                self.marker = []
                self.tracktype = "ungrief"
                self.client.sendServerMessage("Ungrief is on. Place/delete a block to find its owner.")
            elif parts[1] == "off":
                self.tracktype = "normal"
                self.marker = []
                self.question = ""
                self.client.sendServerMessage("Ungrief is off.")
        else:
            self.client.sendServerMessage("You need to specify 'on' or 'off'.")
    
    def chat(self, message):
        if self.tracktype == "ungrief":
            if not self.question == "":
                if "yes".find(message.lower()) >= 0:
                    self.undoname(str(self.marker[3]))
                    self.question = ""
                    return True
                elif "no".find(message.lower()) >= 0:
                    self.marker = []
                    self.question = ""
                    return True
                else:
                    self.client.sendSplitServerMessage("You need to answer the question with 'yes', 'no' or a time.")
                    self.client.sendSplitServerMessage("Time is ment to identify how far back to go. (i.e. 5 min or 1 hour or 3 day) NO MIXING TERMS")
                    self.client.sendServerMessage(self.question)
                    return True

    def undoname(self, player, filter = None):
        newlist = set()
        blocklist = self.client.world.BlockEngine.readd(player, "name", filter)
        #print blocklist
        for item in blocklist:
            x, y, z = self.client.world.blockstore.get_coords(item[0])
            newlist.add((x, y, z, chr(item[1])))
        #print newlist
        self.restore(newlist)

    def undodate(self, start_date, end_date, player = None):
        #print "do something"

    def restore(self, blocklist): # blocklist format: (x, y, z, chr(block))
        # Draw all the blocks on, I guess
        # We use a generator so we can slowly release the blocks
        # We also keep world as a local so they can't change worlds and affect the new one
        world = self.client.world
        def generate_changes():
            for i, j, k, block in blocklist:
                #print i, j, k, block
                if not self.client.AllowedToBuild(i, j, k) and not overriderank:
                    return
                rx = i
                ry = j
                rz = k
                try:
                    world[rx, ry, rz] = block
                    self.client.queueTask(TASK_BLOCKSET, (rx, ry, rz, block), world=world)
                    self.client.sendBlock(rx, ry, rz, block)
                except AssertionError:
                    self.client.sendServerMessage("Out of bounds paste error.")
                    return
                yield
        # Now, set up a loop delayed by the reactor
        block_iter = iter(generate_changes())
        def do_step():
            # Do 10 blocks
            try:
                for x in range(10):
                    block_iter.next()
                reactor.callLater(0.01, do_step)
            except StopIteration:
                self.client.sendServerMessage("Your undo just completed.")
        do_step()

    def highlight(self, x, y, z, x2, y2, z2):
        block = chr(globals()['BLOCK_STILLWATER'])
        if x > x2:
            x, x2 = x2, x
        if y > y2:
            y, y2 = y2, y
        if z > z2:
            z, z2 = z2, z
        x-=1
        y-=1
        z-=1
        x2+=1
        y2+=1
        z2+=1
        for i in range(x, x2+1):
            self.client.sendPacked(TYPE_BLOCKSET, i, y, z, block)
            self.client.sendPacked(TYPE_BLOCKSET, i, y2, z, block)
            self.client.sendPacked(TYPE_BLOCKSET, i, y, z2, block)
            self.client.sendPacked(TYPE_BLOCKSET, i, y2, z2, block)
        for j in range(y, y2+1):
            self.client.sendPacked(TYPE_BLOCKSET, x, j, z, block)
            self.client.sendPacked(TYPE_BLOCKSET, x2, j, z, block)
            self.client.sendPacked(TYPE_BLOCKSET, x, j, z2, block)
            self.client.sendPacked(TYPE_BLOCKSET, x2, j, z2, block)
        for k in range(z, z2+1):
            self.client.sendPacked(TYPE_BLOCKSET, x, y, k, block)
            self.client.sendPacked(TYPE_BLOCKSET, x2, y, k, block)
            self.client.sendPacked(TYPE_BLOCKSET, x, y2, k, block)
            self.client.sendPacked(TYPE_BLOCKSET, x2, y2, k, block)

    def dehighlight(self, x, y, z, x2, y2, z2):
        block = chr(globals()['BLOCK_AIR'])
        if x > x2:
            x, x2 = x2, x
        if y > y2:
            y, y2 = y2, y
        if z > z2:
            z, z2 = z2, z
        x-=1
        y-=1
        z-=1
        x2+=1
        y2+=1
        z2+=1
        world = self.client.world
        for i in range(x, x2+1):
            self.client.sendPacked(TYPE_BLOCKSET, i, y, z, world.blockstore.raw_blocks[world.blockstore.get_offset(i, y, z)])
            self.client.sendPacked(TYPE_BLOCKSET, i, y2, z, world.blockstore.raw_blocks[world.blockstore.get_offset(i, y2, z)])
            self.client.sendPacked(TYPE_BLOCKSET, i, y, z2, world.blockstore.raw_blocks[world.blockstore.get_offset(i, y, z2)])
            self.client.sendPacked(TYPE_BLOCKSET, i, y2, z2, world.blockstore.raw_blocks[world.blockstore.get_offset(i, y2, z2)])
        for j in range(y, y2+1):
            self.client.sendPacked(TYPE_BLOCKSET, x, j, z, world.blockstore.raw_blocks[world.blockstore.get_offset(x, j, z)])
            self.client.sendPacked(TYPE_BLOCKSET, x2, j, z, world.blockstore.raw_blocks[world.blockstore.get_offset(x2, j, z)])
            self.client.sendPacked(TYPE_BLOCKSET, x, j, z2, world.blockstore.raw_blocks[world.blockstore.get_offset(x, j, z2)])
            self.client.sendPacked(TYPE_BLOCKSET, x2, j, z2, world.blockstore.raw_blocks[world.blockstore.get_offset(x2, j, z2)])
        for k in range(z, z2+1):
            self.client.sendPacked(TYPE_BLOCKSET, x, y, k, world.blockstore.raw_blocks[world.blockstore.get_offset(x, y, k)])
            self.client.sendPacked(TYPE_BLOCKSET, x2, y, k, world.blockstore.raw_blocks[world.blockstore.get_offset(x2, y, k)])
            self.client.sendPacked(TYPE_BLOCKSET, x, y2, k, world.blockstore.raw_blocks[world.blockstore.get_offset(x, y2, k)])
            self.client.sendPacked(TYPE_BLOCKSET, x2, y2, k, world.blockstore.raw_blocks[world.blockstore.get_offset(x2, y2, k)])

#def trace():
#     #make sure player typed in stuff
#     try:
#          username = parts[1]
#     except:
#          servermessage("Please type in a players name.")
#     ghostblocks = self.client.blockengine.readname(username)
#     world = self.client.world
#     offset = []
#     #Now sort through the stuff we get
#     for entries in ghostblocks:
#          offset.append( entries[0])
#          x, y, z = whateverfunctiontogetcoordinatesfromoffsets(offset)
#          clientsideblockplace(x,y,z,Stillwaterhex,world=world)

#def undo():
#     #Get the name and number
#     if Len(parts) > 2:
#          try:
#               name = parts[1]
#               number = parts[2]
#          except:
#               sendservermessage("Please include all the details.")
#     #now that we've done that, get the blocks the target placed
#     userblocks = self.client.world.BlockEngine.readname(name)
#     offset = []
#     #now sort through info
#     for entry in userblocks:
#          coordinates = offsettocoordinate(entry[0])
#          blocktype = chr(entry[1])
#          placeblock(coordinates,blocktype,world=world
#          sendtoblockstore[coordinates,blocktype]
#          self.reactor.calllator(.1)
