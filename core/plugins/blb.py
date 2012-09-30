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
import threading
from reqs.twisted.internet import reactor
from core.plugins import ProtocolPlugin
from core.decorators import *
from core.constants import *

class BlbPlugin(ProtocolPlugin):

    commands = {
        "z": "commandBlb",
        "blb": "commandBlb",
        "draw": "commandBlb",
        "cuboid": "commandBlb",
        "cub": "commandBlb",
        "box": "commandBlb",
        "bhb": "commandHBlb",
        "hbox": "commandHBlb",
        "bwb": "commandWBlb",
        "bcb": "commandBcb",
        "bhcb": "commandBhcb",
        "bfb": "commandFBlb",
        "newblb": "commandNBlb",
        "oblb": "commandOneBlb",
        "bob": "commandOneBlb",
        "bxb": "commandBxb",
        "xbtb": "commandXBtb",
        "zbtb": "commandZBtb",
        "bwcb": "commandBwcb",
    }
    
    def getBuildLimit(self, overriderank):
        if self.client.isDirectorPlus() or overriderank:
            return self.client.factory.build_director
        elif self.client.isAdmin() or self.client.isCoder():
            return self.client.factory.build_admin
        elif self.client.isMod():
            return self.client.factory.build_mod
        elif self.client.isOp() or self.client.isWorldOwner():
            return self.client.factory.build_op
        else:
            return self.client.factory.build_other

    @build_list
    @builder_only
    def commandOneBlb(self, parts, fromloc, overriderank):
        "/bob blockname [x y z] - Builder\nAliases: oblb\nSets block to blocktype.\nClick 1 block then do the command."
        if len(parts) < 5 and len(parts) != 2:
            self.client.sendServerMessage("Please enter a type (and possibly a coord triple)")
        else:
            block = self.client.GetBlockValue(parts[1])
            if block == None:
                return
            # If they only provided the type argument, use the last block place
            if len(parts) == 2:
                try:
                    x, y, z = self.client.last_block_changes[0]
                except IndexError:
                    self.client.sendServerMessage("You have not clicked a block yet.")
                    return
            else:
                try:
                    x = int(parts[2])
                    y = int(parts[3])
                    z = int(parts[4])
                except ValueError:
                    self.client.sendServerMessage("All coordinate parameters must be integers.")
                    return
            try:
                if not self.client.AllowedToBuild(x, y, z) and not overriderank:
                    return
                self.client.world[x, y, z] = block
                self.client.runHook("blockchange", x, y, z, ord(block), ord(block), fromloc)
                self.client.queueTask(TASK_BLOCKSET, (x, y, z, block), world=self.client.world)
                self.client.sendBlock(x, y, z, block)
            except AssertionError:
                self.client.sendErrorMessage("Out of bounds bob error.")
                return
            else:
                if fromloc == "user":
                    self.client.sendServerMessage("Your bob just finished.")

    @build_list
    @director_only
    def commandNBlb(self, parts, fromloc, overriderank):
        "/newblb blockname [x y z x2 y2 z2] - Director\nSets all blocks in this area to block.\nClick 2 corners then do the command."
        if len(parts) < 8 and len(parts) != 2:
            self.client.sendServerMessage("Please enter a type (and possibly two coord triples)")
        else:
            block = self.client.GetBlockValue(parts[1])
            if block == None:
                return
            # If they only provided the type argument, use the last two block places
            if len(parts) == 2:
                try:
                    x, y, z = self.client.last_block_changes[0]
                    x2, y2, z2 = self.client.last_block_changes[1]
                except IndexError:
                    self.client.sendServerMessage("You have not clicked two corners yet.")
                    return
            else:
                try:
                    x = int(parts[2])
                    y = int(parts[3])
                    z = int(parts[4])
                    x2 = int(parts[5])
                    y2 = int(parts[6])
                    z2 = int(parts[7])
                except ValueError:
                    self.client.sendServerMessage("All coordinate parameters must be integers.")
                    return
            if x > x2:
                x, x2 = x2, x
            if y > y2:
                y, y2 = y2, y
            if z > z2:
                z, z2 = z2, z
            limit = self.getBuildLimit(overriderank)
            realLimit = (x2 - x) * (y2 - y) * (z2 - z) 
            if realLimit > limit:
                self.client.sendErrorMessage("Sorry, that area is too big for you to blb.")
                return
            world = self.client.world
            if realLimit >= 45565: # To test it out first, will try a bigger one later - tyteen
                def doBlocks():
                    # This implements 2 new things: Respawn method and try-the-whole-loop.
                    # Since the loop stops when an AssertionErrors pops up, so we just
                    # go and check the whole loop, so there isn't a need to try the block
                    # Everytime.
                    # The respawn method changes the BLB proceedures as follows:
                    # 1. Change the block but DOES NOT send it to users
                    # 2. Respawn the users in world
                    # Since this method does not send blocks one by one but respawns to download
                    # the map at one time, it saves time.
                    # All clients will get respawned too.
                    # Credits to UberFoX for this idea. Thanks Stacy!
                    try:
                        for i in range(x, x2+1):
                            for j in range(y, y2+1):
                                for k in range(z, z2+1):
                                    if not self.client.AllowedToBuild(i, j, k) and not overriderank:
                                        return
                                    world[i, j, k] = block
                        self.client.sendServerMessage("BLB finished. Respawning...")
                        return True
                    except AssertionError:
                        self.client.sendErrorMessage("Out of bounds blb error.")
                        return
                threading.Thread(target=doBlocks).start()
                # Now the fun part. Respawn them all!
                for client in world.clients:
                    self.client.queueTask(TASK_INSTANTRESPAWN, self.client.username, world=world)
                if fromloc == "user":
                    self.client.sendServerMessage("Your blb just completed.")
            else:
                def generate_changes():
                    try:
                        for i in range(x, x2+1):
                            for j in range(y, y2+1):
                                for k in range(z, z2+1):
                                    if not self.client.AllowedToBuild(i, j, k) and not overriderank:
                                        return
                                    world[i, j, k] = block
                                    self.client.runHook("blockchange", x, y, z, ord(block), ord(block), fromloc)
                                    self.client.queueTask(TASK_BLOCKSET, (i, j, k, block), world=world)
                                    self.client.sendBlock(i, j, k, block)
                                    yield
                    except AssertionError:
                        self.client.sendErrorMessage("Out of bounds blb error.")
                        return
                block_iter = iter(generate_changes())
                def do_step():
                    try:
                        for x in range(10):
                            block_iter.next()
                        reactor.callLater(0.01, do_step)
                    except StopIteration:
                        if fromloc == "user":
                            self.client.sendServerMessage("Your blb just completed.")
                        pass
                do_step()
            
    @build_list
    @builder_only
    def commandBlb(self, parts, fromloc, overriderank):
        "/blb blockname [x y z x2 y2 z2] - Builder\nAliases: box, cub, cuboid, draw\nSets all blocks in this area to block.\nClick 2 corners then do the command."
        if len(parts) < 8 and len(parts) != 2:
            self.client.sendServerMessage("Please enter a type (and possibly two coord triples)")
        else:
            block = self.client.GetBlockValue(parts[1])
            if block == None:
                return
            # If they only provided the type argument, use the last two block places
            if len(parts) == 2:
                try:
                    x, y, z = self.client.last_block_changes[0]
                    x2, y2, z2 = self.client.last_block_changes[1]
                except IndexError:
                    self.client.sendServerMessage("You have not clicked two corners yet.")
                    return
            else:
                try:
                    x = int(parts[2])
                    y = int(parts[3])
                    z = int(parts[4])
                    x2 = int(parts[5])
                    y2 = int(parts[6])
                    z2 = int(parts[7])
                except ValueError:
                    self.client.sendServerMessage("All coordinate parameters must be integers.")
                    return
            if x > x2:
                x, x2 = x2, x
            if y > y2:
                y, y2 = y2, y
            if z > z2:
                z, z2 = z2, z
            limit = self.getBuildLimit(overriderank)
            # Stop them doing silly things
            if (x2 - x) * (y2 - y) * (z2 - z) > limit:
                self.client.sendErrorMessage("Sorry, that area is too big for you to blb.")
                return
            # Draw all the blocks on, I guess
            # We use a generator so we can slowly release the blocks
            # We also keep world as a local so they can't change worlds and affect the new one
            world = self.client.world
            def generate_changes():
                try:
                    for i in range(x, x2+1):
                        for j in range(y, y2+1):
                            for k in range(z, z2+1):
                                if not self.client.AllowedToBuild(i, j, k) and not overriderank:
                                    return
                                check_offset = world.blockstore.get_offset(i, j, k)
                                existingBlock = world.blockstore.raw_blocks[check_offset]
                                if existingBlock != block:
                                    world[i, j, k] = block
                                    self.client.runHook("blockchange", x, y, z, ord(block), ord(block), fromloc)
                                    self.client.queueTask(TASK_BLOCKSET, (i, j, k, block), world)
                                    self.client.sendBlock(i, j, k, block)
                                    yield
                except AssertionError:
                    self.client.sendErrorMessage("Out of bounds blb error.")
                    return
            # Now, set up a loop delayed by the reactor
            block_iter = iter(generate_changes())
            def do_step():
                # Do 10 blocks
                try:
                    for x in range(10): # 10 blocks at a time, 10 blocks per tenths of a second, 100 blocks a second
                        block_iter.next()
                    reactor.callLater(0.01, do_step) # This is how long (in seconds) it waits to run another 10 blocks
                except StopIteration:
                    if fromloc == "user":
                        self.client.sendServerMessage("Your blb just completed.")
                    pass
            do_step()

    @build_list
    @builder_only
    def commandHBlb(self, parts, fromloc, overriderank):
        "/bhb blockname [x y z x2 y2 z2] - Builder\nAliases: hbox\nSets all blocks in this area to block, hollow."
        if len(parts) < 8 and len(parts) != 2:
            self.client.sendServerMessage("Please enter a block type")
        else:
            block = self.client.GetBlockValue(parts[1])
            if block == None:
                return
            # If they only provided the type argument, use the last two block places
            if len(parts) == 2:
                try:
                    x, y, z = self.client.last_block_changes[0]
                    x2, y2, z2 = self.client.last_block_changes[1]
                except IndexError:
                    self.client.sendServerMessage("You have not clicked two corners yet.")
                    return
            else:
                try:
                    x = int(parts[2])
                    y = int(parts[3])
                    z = int(parts[4])
                    x2 = int(parts[5])
                    y2 = int(parts[6])
                    z2 = int(parts[7])
                except ValueError:
                    self.client.sendServerMessage("All coordinate parameters must be integers.")
                    return
            if x > x2:
                x, x2 = x2, x
            if y > y2:
                y, y2 = y2, y
            if z > z2:
                z, z2 = z2, z
            limit = self.getBuildLimit(overriderank)
            # Stop them doing silly things
            if (x2 - x) * (y2 - y) * (z2 - z) > limit:
                self.client.sendErrorMessage("Sorry, that area is too big for you to bhb.")
                return
            # Draw all the blocks on, I guess
            # We use a generator so we can slowly release the blocks
            # We also keep world as a local so they can't change worlds and affect the new one
            world = self.client.world
            def generate_changes():
                try:
                    for i in range(x, x2+1):
                        for j in range(y, y2+1):
                            for k in range(z, z2+1):
                                if not self.client.AllowedToBuild(i, j, k) and not overriderank:
                                    return
                                if i==x or i==x2 or j==y or j==y2 or k==z or k==z2:
                                    check_offset = world.blockstore.get_offset(i, j, k)
                                    existingBlock = world.blockstore.raw_blocks[check_offset]
                                    if existingBlock != block:
                                        world[i, j, k] = block
                                        self.client.runHook("blockchange", x, y, z, ord(block), ord(block), fromloc)
                                        self.client.queueTask(TASK_BLOCKSET, (i, j, k, block), world)
                                        self.client.sendBlock(i, j, k, block)
                                        yield
                except AssertionError:
                    self.client.sendErrorMessage("Out of bounds bhb error.")
                    return
            # Now, set up a loop delayed by the reactor
            block_iter = iter(generate_changes())
            def do_step():
                # Do 10 blocks
                try:
                    for x in range(10): # 10 blocks at a time, 10 blocks per tenths of a second, 100 blocks a second
                        block_iter.next()
                    reactor.callLater(0.01, do_step) # This is how long (in seconds) it waits to run another 10 blocks
                except StopIteration:
                    if fromloc == "user":
                        self.client.sendServerMessage("Your bhb just completed.")
                    pass
            do_step()

    @build_list
    @builder_only
    def commandWBlb(self, parts, fromloc, overriderank):
        "/bwb blockname [x y z x2 y2 z2] - Builder\nBuilds four walls between the two areas.\nHollow, with no roof or floor."
        if len(parts) < 8 and len(parts) != 2:
            self.client.sendServerMessage("Please enter a block type")
        else:
            block = self.client.GetBlockValue(parts[1])
            if block == None:
                return
            # If they only provided the type argument, use the last two block places
            if len(parts) == 2:
                try:
                    x, y, z = self.client.last_block_changes[0]
                    x2, y2, z2 = self.client.last_block_changes[1]
                except IndexError:
                    self.client.sendServerMessage("You have not clicked two corners yet.")
                    return
            else:
                try:
                    x = int(parts[2])
                    y = int(parts[3])
                    z = int(parts[4])
                    x2 = int(parts[5])
                    y2 = int(parts[6])
                    z2 = int(parts[7])
                except ValueError:
                    self.client.sendServerMessage("All coordinate parameters must be integers.")
                    return
            if x > x2:
                x, x2 = x2, x
            if y > y2:
                y, y2 = y2, y
            if z > z2:
                z, z2 = z2, z
            limit = self.getBuildLimit(overriderank)
            # Stop them doing silly things
            if (x2 - x) * (y2 - y) * (z2 - z) > limit:
                self.client.sendErrorMessage("Sorry, that area is too big for you to bwb.")
                return
            # Draw all the blocks on, I guess
            # We use a generator so we can slowly release the blocks
            # We also keep world as a local so they can't change worlds and affect the new one
            world = self.client.world
            def generate_changes():
                try:
                    for i in range(x, x2+1):
                        for j in range(y, y2+1):
                            for k in range(z, z2+1):
                                if not self.client.AllowedToBuild(i, j, k) and not overriderank:
                                    return
                                if i==x or i==x2 or k==z or k==z2:
                                    check_offset = world.blockstore.get_offset(i, j, k)
                                    existingBlock = world.blockstore.raw_blocks[check_offset]
                                    if existingBlock != block:
                                        world[i, j, k] = block
                                        self.client.runHook("blockchange", x, y, z, ord(block), ord(block), fromloc)
                                        self.client.queueTask(TASK_BLOCKSET, (i, j, k, block), world)
                                        self.client.sendBlock(i, j, k, block)
                                        yield
                except AssertionError:
                    self.client.sendErrorMessage("Out of bounds bwb error.")
                    return
            # Now, set up a loop delayed by the reactor
            block_iter = iter(generate_changes())
            def do_step():
                # Do 10 blocks
                try:
                    for x in range(10): # 10 blocks at a time, 10 blocks per tenths of a second, 100 blocks a second
                        block_iter.next()
                    reactor.callLater(0.01, do_step) # This is how long (in seconds) it waits to run another 10 blocks
                except StopIteration:
                    if fromloc == "user":
                        self.client.sendServerMessage("Your bwb just completed.")
                    pass
            do_step()

    @build_list
    @builder_only
    def commandBcb(self, parts, fromloc, overriderank):
        "/bcb blockname blockname2 [x y z x2 y2 z2] - Builder\nSets all blocks in this area to block, checkered."
        if len(parts) < 9 and len(parts) != 3:
            self.client.sendServerMessage("Please enter two types (and possibly two coord triples)")
        else:
            # Try getting block2 as a direct integer type.
            try:
                block2 = chr(int(parts[2]))
            except ValueError:
                # OK, try a symbolic type.
                try:
                    block2 = chr(globals()['BLOCK_%s' % parts[2].upper()])
                except KeyError:
                    self.client.sendErrorMessage("'%s' is not a valid block type." % parts[2])
                    return
            # Try getting the block as a direct integer type.
            try:
                block = chr(int(parts[1]))
            except ValueError:
                # OK, try a symbolic type.
                try:
                    block = chr(globals()['BLOCK_%s' % parts[1].upper()])
                except KeyError:
                    self.client.sendErrorMessage("'%s' is not a valid block type." % parts[1])
                    return
            # Check the block is valid
            if ord(block) > 49:
                self.client.sendErrorMessage("'%s' is not a valid block type." % parts[1])
                return
            op_blocks = [BLOCK_SOLID, BLOCK_WATER, BLOCK_LAVA]
            if ord(block) in op_blocks and not self.client.isOpPlus():
                self.client.sendServerMessage("Sorry, but you can't use that block.")
                return
            # Check that block2 is valid
            if ord(block2) > 49:
                self.client.sendErrorMessage("'%s' is not a valid block type." % parts[1])
                return
            if ord(block2) == 7:
                try:
                    username = self.client.factory.usernames[self.client.username.lower()]
                except:
                    self.client.sendErrorMessage("ERROR Identity could not be confirmed")
                    return
                if username.isMember() or username.isOpPlus():
                    pass
                else:
                    self.client.sendErrorMessage("Solid is op-only")
                    return
            # If they only provided the type argument, use the last two block places
            if len(parts) == 3:
                try:
                    x, y, z = self.client.last_block_changes[0]
                    x2, y2, z2 = self.client.last_block_changes[1]
                except IndexError:
                    self.client.sendServerMessage("You have not clicked two corners yet.")
                    return
            else:
                try:
                    x = int(parts[3])
                    y = int(parts[4])
                    z = int(parts[5])
                    x2 = int(parts[6])
                    y2 = int(parts[7])
                    z2 = int(parts[8])
                except ValueError:
                    self.client.sendServerMessage("All coordinate parameters must be integers.")
                    return
            if x > x2:
                x, x2 = x2, x
            if y > y2:
                y, y2 = y2, y
            if z > z2:
                z, z2 = z2, z
            limit = self.getBuildLimit(overriderank)
            # Stop them doing silly things
            if (x2 - x) * (y2 - y) * (z2 - z) > limit:
                self.client.sendErrorMessage("Sorry, that area is too big for you to bcb.")
                return
            # Draw all the blocks on, I guess
            # We use a generator so we can slowly release the blocks
            # We also keep world as a local so they can't change worlds and affect the new one
            world = self.client.world
            def generate_changes():
                try:
                    for i in range(x, x2+1):
                        for j in range(y, y2+1):
                            for k in range(z, z2+1):
                                if not self.client.AllowedToBuild(i, j, k):
                                    return
                                if (i+j+k)%2 == 0:
                                    curNewBlock = block2
                                else:
                                    curNewBlock = block
                                check_offset = world.blockstore.get_offset(i, j, k)
                                existingBlock = world.blockstore.raw_blocks[check_offset]
                                if existingBlock != curNewBlock:
                                    world[i, j, k] = curNewBlock
                                    self.client.runHook("blockchange", x, y, z, ord(curNewBlock), ord(curNewBlock), fromloc)
                                    self.client.queueTask(TASK_BLOCKSET, (i, j, k, curNewBlock), world)
                                    self.client.sendBlock(i, j, k, curNewBlock)
                                    yield
                except AssertionError:
                    self.client.sendErrorMessage("Out of bounds bcb error.")
                    return
            # Now, set up a loop delayed by the reactor
            block_iter = iter(generate_changes())
            def do_step():
                # Do 10 blocks
                try:
                    for x in range(10): # 10 blocks at a time, 10 blocks per tenths of a second, 100 blocks a second
                        block_iter.next()
                    reactor.callLater(0.01, do_step) # This is how long (in seconds) it waits to run another 10 blocks
                except StopIteration:
                    if fromloc == "user":
                        self.client.sendServerMessage("Your bcb just completed.")
                    pass
            do_step()

    @build_list
    @builder_only
    def commandBhcb(self, parts, fromloc, overriderank):
        "/bhcb blockname blockname2 [x y z x2 y2 z2] - Builder\nSets all blocks in this area to blocks, checkered hollow."
        if len(parts) < 9 and len(parts) != 3:
            self.client.sendServerMessage("Please enter two block types")
        else:
            # Try getting block2 as a direct integer type.
            try:
                block2 = chr(int(parts[2]))
            except ValueError:
                # OK, try a symbolic type.
                try:
                    block2 = chr(globals()['BLOCK_%s' % parts[2].upper()])
                except KeyError:
                    self.client.sendErrorMessage("'%s' is not a valid block type." % parts[2])
                    return
            # Try getting the block as a direct integer type.
            try:
                block = chr(int(parts[1]))
            except ValueError:
                # OK, try a symbolic type.
                try:
                    block = chr(globals()['BLOCK_%s' % parts[1].upper()])
                except KeyError:
                    self.client.sendErrorMessage("'%s' is not a valid block type." % parts[1])
                    return
            # Check the block is valid
            if ord(block) > 49:
                self.client.sendErrorMessage("'%s' is not a valid block type." % parts[1])
                return
            op_blocks = [BLOCK_SOLID, BLOCK_WATER, BLOCK_LAVA]
            if ord(block) in op_blocks and not self.client.isOpPlus():
                self.client.sendErrorMessage("Sorry, but you can't use that block.")
                return
            # If they only provided the type argument, use the last two block places
            if len(parts) == 3:
                try:
                    x, y, z = self.client.last_block_changes[0]
                    x2, y2, z2 = self.client.last_block_changes[1]
                except IndexError:
                    self.client.sendErrorMessage("You have not clicked two corners yet.")
                    return
            else:
                try:
                    x = int(parts[2])
                    y = int(parts[3])
                    z = int(parts[4])
                    x2 = int(parts[5])
                    y2 = int(parts[6])
                    z2 = int(parts[7])
                except ValueError:
                    self.client.sendServerMessage("All coordinate parameters must be integers.")
                    return
            if x > x2:
                x, x2 = x2, x
            if y > y2:
                y, y2 = y2, y
            if z > z2:
                z, z2 = z2, z
            limit = self.getBuildLimit(overriderank)
            # Stop them doing silly things
            if (x2 - x) * (y2 - y) * (z2 - z) > limit:
                self.client.sendErrorMessage("Sorry, that area is too big for you to bhcb.")
                return
            # Draw all the blocks on, I guess
            # We use a generator so we can slowly release the blocks
            # We also keep world as a local so they can't change worlds and affect the new one
            world = self.client.world
            def generate_changes():
                try:
                    for i in range(x, x2+1):
                        for j in range(y, y2+1):
                            for k in range(z, z2+1):
                                if not self.client.AllowedToBuild(i, j, k):
                                    return
                                if i==x or i==x2 or j==y or j==y2 or k==z or k==z2:
                                    if (i+j+k)%2 == 0:
                                        curNewBlock = block2
                                    else:
                                        curNewBlock = block
                                    check_offset = world.blockstore.get_offset(i, j, k)
                                    existingBlock = world.blockstore.raw_blocks[check_offset]
                                    if existingBlock != curNewBlock:
                                        world[i, j, k] = curNewBlock
                                        self.client.runHook("blockchange", x, y, z, ord(curNewBlock), ord(curNewBlock), fromloc)
                                        self.client.queueTask(TASK_BLOCKSET, (i, j, k, curNewBlock), world)
                                        self.client.sendBlock(i, j, k, curNewBlock)
                                        yield
                except AssertionError:
                    self.client.sendErrorMessage("Out of bounds bhcb error.")
                    return
            # Now, set up a loop delayed by the reactor
            block_iter = iter(generate_changes())
            def do_step():
                # Do 10 blocks
                try:
                    for x in range(10): # 10 blocks at a time, 10 blocks per tenths of a second, 100 blocks a second
                        block_iter.next()
                    reactor.callLater(0.01, do_step) # This is how long (in seconds) it waits to run another 10 blocks
                except StopIteration:
                    if fromloc == "user":
                        self.client.sendServerMessage("Your bhcb just completed.")
                    pass
            do_step()

    @build_list
    @builder_only
    def commandFBlb(self, parts, fromloc, overriderank):
        "/bfb blockname [x y z x2 y2 z2] - Builder\nSets all blocks in this area to block, wireframe."
        if len(parts) < 8 and len(parts) != 2:
            self.client.sendServerMessage("Please enter a block type")
        else:
            # Try getting the block as a direct integer type.
            try:
                block = chr(int(parts[1]))
            except ValueError:
                # OK, try a symbolic type.
                try:
                    block = chr(globals()['BLOCK_%s' % parts[1].upper()])
                except KeyError:
                    self.client.sendErrorMessage("'%s' is not a valid block type." % parts[1])
                    return
            # Check the block is valid
            if ord(block) > 49:
                self.client.sendErrorMessage("'%s' is not a valid block type." % parts[1])
                return
            op_blocks = [BLOCK_SOLID, BLOCK_WATER, BLOCK_LAVA]
            if ord(block) in op_blocks and not self.client.isOpPlus():
                self.client.sendErrorMessage("Sorry, but you can't use that block.")
                return
            # If they only provided the type argument, use the last two block places
            if len(parts) == 2:
                try:
                    x, y, z = self.client.last_block_changes[0]
                    x2, y2, z2 = self.client.last_block_changes[1]
                except IndexError:
                    self.client.sendServerMessage("You have not clicked two corners yet.")
                    return
            else:
                try:
                    x = int(parts[2])
                    y = int(parts[3])
                    z = int(parts[4])
                    x2 = int(parts[5])
                    y2 = int(parts[6])
                    z2 = int(parts[7])
                except ValueError:
                    self.client.sendServerMessage("All coordinate parameters must be integers.")
                    return
            if x > x2:
                x, x2 = x2, x
            if y > y2:
                y, y2 = y2, y
            if z > z2:
                z, z2 = z2, z
            limit = self.getBuildLimit(overriderank)
            # Stop them doing silly things
            if (x2 - x) * (y2 - y) * (z2 - z) > limit:
                self.client.sendErrorMessage("Sorry, that area is too big for you to bfb.")
                return
            # Draw all the blocks on, I guess
            # We use a generator so we can slowly release the blocks
            # We also keep world as a local so they can't change worlds and affect the new one
            world = self.client.world
            def generate_changes():
                try:
                    for i in range(x, x2+1):
                        for j in range(y, y2+1):
                            for k in range(z, z2+1):
                                if not self.client.AllowedToBuild(i, j, k):
                                    return
                                if (i==x and j==y) or (i==x2 and j==y2) or (j==y2 and k==z2) or (i==x2 and k==z2) or (j==y and k==z) or (i==x and k==z) or (i==x and k==z2) or (j==y and k==z2) or (i==x2 and k==z) or (j==y2 and k==z) or (i==x and j==y2) or (i==x2 and j==y):
                                    check_offset = world.blockstore.get_offset(i, j, k)
                                    existingBlock = world.blockstore.raw_blocks[check_offset]
                                    if existingBlock != block:
                                        world[i, j, k] = block
                                        self.client.runHook("blockchange", x, y, z, ord(block), ord(block), fromloc)
                                        self.client.queueTask(TASK_BLOCKSET, (i, j, k, block), world)
                                        self.client.sendBlock(i, j, k, block)
                                        yield
                except AssertionError:
                    self.client.sendErrorMessage("Out of bounds bfb error.")
                    return
            # Now, set up a loop delayed by the reactor
            block_iter = iter(generate_changes())
            def do_step():
                # Do 10 blocks
                try:
                    for x in range(10): # 10 blocks at a time, 10 blocks per tenths of a second, 100 blocks a second
                        block_iter.next()
                    reactor.callLater(0.01, do_step) # This is how long (in seconds) it waits to run another 10 blocks
                except StopIteration:
                    if fromloc == "user":
                        self.client.sendServerMessage("Your bfb just completed.")
                    pass
            do_step()

    @build_list
    @builder_only
    def commandBxb(self, parts, fromloc, overriderank):
        "/bxb blockname [x y z x2 y2 z2] - Builder\nSets all blocks in this area to block, cross style."
        if len(parts) < 8 and len(parts) != 2:
            self.client.sendServerMessage("Please enter a block type")
        else:
            try:
                block = chr(int(parts[1]))
            except ValueError:
                try:
                    block = chr(globals()['BLOCK_%s' % parts[1].upper()])
                except KeyError:
                    self.client.sendErrorMessage("'%s' is not a valid block type." % parts[1])
                    return
            if ord(block) > 49:
                self.client.sendErrorMessage("'%s' is not a valid block type." % parts[1])
                return
            op_blocks = [BLOCK_SOLID, BLOCK_WATER, BLOCK_LAVA]
            if ord(block) in op_blocks and not self.client.isOpPlus():
                self.client.sendErrorMessage("Sorry, but you can't use that block.")
                return
            if len(parts) == 2:
                try:
                    x, y, z = self.client.last_block_changes[0]
                    x2, y2, z2 = self.client.last_block_changes[1]
                except IndexError:
                    self.client.sendServerMessage("You have not clicked two corners yet.")
                    return
            else:
                try:
                    x = int(parts[2])
                    y = int(parts[3])
                    z = int(parts[4])
                    x2 = int(parts[5])
                    y2 = int(parts[6])
                    z2 = int(parts[7])
                except ValueError:
                    self.client.sendServerMessage("All parameters must be integers")
                    return
            if x > x2:
                x, x2 = x2, x
            if y > y2:
                y, y2 = y2, y
            if z > z2:
                z, z2 = z2, z
            limit = self.getBuildLimit(overriderank)
            if (x2 - x) * (y2 - y) * (z2 - z) > limit:
                self.client.sendErrorMessage("Sorry, that area is too big for you to bxb.")
                return
            world = self.client.world
            def generate_changes():
                try:
                    for i in range(x, x2+1):
                        for j in range(y, y2+1):
                            for k in range(z, z2+1):
                                if not self.client.AllowedToBuild(i, j, k):
                                    return
                                if (i==(x+x2)/2 and j==y) or (i==(x+x2)/2 and j==y2) or (i==x and j==(y+y2)/2) or (i==x2 and j==(y+y2)/2) or (j==y and k==(z+z2)/2) or (i==(x+x2)/2 and k==z) or (j==(y+y2)/2 and k==z) or (i==x2 and k==(z+z2)/2) or (i==(x+x2)/2 and k==z2) or (j==y2 and k==(z+z2)/2) or (i==x and k==(z+z2)/2) or (j==(y+y2)/2 and k==z2) or (i==(x+x2)/2 and j==y) or (i==x2 and j==(y+y2)/2):
                                    check_offset = world.blockstore.get_offset(i, j, k)
                                    existingBlock = world.blockstore.raw_blocks[check_offset]
                                    if existingBlock != block:
                                        world[i, j, k] = block
                                        self.client.runHook("blockchange", x, y, z, ord(block), ord(block), fromloc)
                                        self.client.queueTask(TASK_BLOCKSET, (i, j, k, block), world)
                                        self.client.sendBlock(i, j, k, block)
                                        yield
                except AssertionError:
                    self.client.sendErrorMessage("Out of bounds bxb error.")
                    return
            block_iter = iter(generate_changes())
            def do_step():
                try:
                    for x in range(10):
                        block_iter.next()
                    reactor.callLater(0.01, do_step)
                except StopIteration:
                    if fromloc == "user":
                        self.client.sendServerMessage("Your bxb just completed.")
                    pass
            do_step()

    @build_list
    @builder_only
    def commandBwcb(self, parts, fromloc, overriderank):
        "/bwcb blockname blockname2 [x y z x2 y2 z2] - Builder\nSets all blocks in this area to blocks, checkered walls."
        if len(parts) < 9 and len(parts) != 3:
            self.client.sendServerMessage("Please enter two block types")
        else:
            try:
                block2 = chr(int(parts[2]))
            except ValueError:
                try:
                    block2 = chr(globals()['BLOCK_%s' % parts[2].upper()])
                except KeyError:
                    self.client.sendErrorMessage("'%s' is not a valid block type." % parts[2])
                    return
            try:
                block = chr(int(parts[1]))
            except ValueError:
                try:
                    block = chr(globals()['BLOCK_%s' % parts[1].upper()])
                except KeyError:
                    self.client.sendErrorMessage("'%s' is not a valid block type." % parts[1])
                    return
            if ord(block) > 49:
                self.client.sendServerMessage("'%s' is not a valid block type." % parts[1])
                return
            op_blocks = [BLOCK_SOLID, BLOCK_WATER, BLOCK_LAVA]
            if ord(block) in op_blocks and not self.client.isOpPlus():
                self.client.sendErrorMessage("Sorry, but you can't use that block.")
                return
            if len(parts) == 3:
                try:
                    x, y, z = self.client.last_block_changes[0]
                    x2, y2, z2 = self.client.last_block_changes[1]
                except IndexError:
                    self.client.sendServerMessage("You have not clicked two corners yet.")
                    return
            else:
                try:
                    x = int(parts[2])
                    y = int(parts[3])
                    z = int(parts[4])
                    x2 = int(parts[5])
                    y2 = int(parts[6])
                    z2 = int(parts[7])
                except ValueError:
                    self.client.sendServerMessage("All parameters must be integers")
                    return
            if x > x2:
                x, x2 = x2, x
            if y > y2:
                y, y2 = y2, y
            if z > z2:
                z, z2 = z2, z
            limit = self.getBuildLimit(overriderank)
            if (x2 - x) * (y2 - y) * (z2 - z) > limit:
                self.client.sendErrorMessage("Sorry, that area is too big for you to bwcb.")
                return
            world = self.client.world
            def generate_changes():
                try:
                    for i in range(x, x2+1):
                        for j in range(y, y2+1):
                            for k in range(z, z2+1):
                                if not self.client.AllowedToBuild(i, j, k):
                                    return
                                if i==x or i==x2 or k==z or k==z2:
                                    if (i+j+k)%2 == 0:
                                        curNewBlock = block2
                                    else:
                                        curNewBlock = block
                                    check_offset = world.blockstore.get_offset(i, j, k)
                                    existingBlock = world.blockstore.raw_blocks[check_offset]
                                    if existingBlock != curNewBlock:
                                        world[i, j, k] = curNewBlock
                                        self.client.runHook("blockchange", x, y, z, ord(curNewBlock), ord(curNewBlock), fromloc)
                                        self.client.queueTask(TASK_BLOCKSET, (i, j, k, curNewBlock), world)
                                        self.client.sendBlock(i, j, k, curNewBlock)
                                        yield
                except AssertionError:
                    self.client.sendErrorMessage("Out of bounds bwcb error.")
                    return
            block_iter = iter(generate_changes())
            def do_step():
                try:
                    for x in range(10):
                        block_iter.next()
                    reactor.callLater(0.01, do_step)
                except StopIteration:
                    if fromloc == "user":
                        self.client.sendServerMessage("Your bwcb just completed.")
                    pass
            do_step()

    @build_list
    @builder_only
    def commandXBtb(self, parts, fromloc, overriderank):
        "/xbtb blockname [x y z x2 y2 z2] - Builder\nBuilds a tunnel on the x-axis."
        if len(parts) < 8 and len(parts) != 2:
            self.client.sendServerMessage("Please enter a block type")
        else:
            block = self.client.GetBlockValue(parts[1])
            if block == None:
                return
            if len(parts) == 2:
                try:
                    x, y, z = self.client.last_block_changes[0]
                    x2, y2, z2 = self.client.last_block_changes[1]
                except IndexError:
                    self.client.sendServerMessage("You have not clicked two corners yet.")
                    return
            else:
                try:
                    x = int(parts[2])
                    y = int(parts[3])
                    z = int(parts[4])
                    x2 = int(parts[5])
                    y2 = int(parts[6])
                    z2 = int(parts[7])
                except ValueError:
                    self.client.sendServerMessage("All parameters must be integers")
                    return
            if x > x2:
                x, x2 = x2, x
            if y > y2:
                y, y2 = y2, y
            if z > z2:
                z, z2 = z2, z
            limit = self.getBuildLimit(overriderank)
            if (x2 - x) * (y2 - y) * (z2 - z) > limit:
                self.client.sendErrorMessage("Sorry, that area is too big for you to btb.")
                return
            world = self.client.world
            def generate_changes():
                try:
                    for i in range(x, x2+1):
                        for j in range(y, y2+1):
                            for k in range(z, z2+1):
                                if not self.client.AllowedToBuild(i, j, k) and overriderank==False:
                                    return
                                if i==x or i==x2 or j==y or j==y2:
                                    check_offset = world.blockstore.get_offset(i, j, k)
                                    existingBlock = world.blockstore.raw_blocks[check_offset]
                                    if existingBlock != block:
                                        world[i, j, k] = block
                                        self.client.runHook("blockchange", x, y, z, ord(block), ord(block), fromloc)
                                        self.client.queueTask(TASK_BLOCKSET, (i, j, k, block), world)
                                        self.client.sendBlock(i, j, k, block)
                                        yield
                except AssertionError:
                    self.client.sendServerMessage("Out of bounds btb error.")
                    return
            block_iter = iter(generate_changes())
            def do_step():
                try:
                    for x in range(10):
                        block_iter.next()
                    reactor.callLater(0.01, do_step)
                except StopIteration:
                    if fromloc == "user":
                        self.client.sendServerMessage("Your btb just completed.")
                    pass
            do_step()

    @build_list
    @builder_only
    def commandZBtb(self, parts, fromloc, overriderank):
        "/zbtb blockname [x y z x2 y2 z2] - Builder\nBuilds a tunnel on the z-axis."
        if len(parts) < 8 and len(parts) != 2:
            self.client.sendServerMessage("Please enter a block type")
        else:
            block = self.client.GetBlockValue(parts[1])
            if block == None:
                return
            if len(parts) == 2:
                try:
                    x, y, z = self.client.last_block_changes[0]
                    x2, y2, z2 = self.client.last_block_changes[1]
                except IndexError:
                    self.client.sendServerMessage("You have not clicked two corners yet.")
                    return
            else:
                try:
                    x = int(parts[2])
                    y = int(parts[3])
                    z = int(parts[4])
                    x2 = int(parts[5])
                    y2 = int(parts[6])
                    z2 = int(parts[7])
                except ValueError:
                    self.client.sendServerMessage("All parameters must be integers")
                    return
            if x > x2:
                x, x2 = x2, x
            if y > y2:
                y, y2 = y2, y
            if z > z2:
                z, z2 = z2, z
            limit = self.getBuildLimit(overriderank)
            if (x2 - x) * (y2 - y) * (z2 - z) > limit:
                self.client.sendErrorMessage("Sorry, that area is too big for you to btb.")
                return
            world = self.client.world
            def generate_changes():
                try:
                    for i in range(x, x2+1):
                        for j in range(y, y2+1):
                            for k in range(z, z2+1):
                                if not self.client.AllowedToBuild(i, j, k) and overriderank==False:
                                    return
                                if k==z or k==z2 or j==y or j==y2:
                                    check_offset = world.blockstore.get_offset(i, j, k)
                                    existingBlock = world.blockstore.raw_blocks[check_offset]
                                    if existingBlock != block:
                                        world[i, j, k] = block
                                        self.client.runHook("blockchange", x, y, z, ord(block), ord(block), fromloc)
                                        self.client.queueTask(TASK_BLOCKSET, (i, j, k, block), world)
                                        self.client.sendBlock(i, j, k, block)
                                        yield
                except AssertionError:
                    self.client.sendErrorMessage("Out of bounds btb error.")
                    return
            block_iter = iter(generate_changes())
            def do_step():
                try:
                    for x in range(10):
                        block_iter.next()
                    reactor.callLater(0.01, do_step)
                except StopIteration:
                    if fromloc == "user":
                        self.client.sendServerMessage("Your btb just completed.")
                    pass
            do_step()
