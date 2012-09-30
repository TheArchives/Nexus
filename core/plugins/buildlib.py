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
import threading, math, random, sys
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
        "sphere": "commandSphere",
        "hsphere": "commandHSphere",
        "curve": "commandCurve",
        "line": "commandLine",
        "pyramid": "commandPyramid",
        "csphere": "commandCsphere",
        "circle": "commandCircle",
        "cir": "commandCircle",
        "hcir": "commandHCircle",
        "hcircle": "commandHCircle",
        "hcyl": "commandHCylinder",
        "cyl": "commandCylinder",
        "dome": "commandDome",
        "ellipsoid": "commandEllipsoid",
        "ell": "commandEllipsoid",
        "polytri": "commandPolytri",
        "stairs": "commandStairs",
        "replace": "commandBrep",
        "brep": "commandBrep",
        "creplace": "commandCreplace",
        "crep": "commandCreplace",
        "fill": "commandFill",
        "replacenear": "commandReplaceNear",
        "rn": "commandReplaceNear",
        "dune": "commandDune",
        "hill": "commandHill",
        "hole": "commandHole",
        "lake": "commandLake",
        "mountain": "commandMountain",
        "pit": "commandPit",
        "tree": "commandTree",
        "b3b": "commandBThreeB",
    }

    hooks = {
        "blockchange": "blockChanged",
        "newworld": "newWorld",
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

    def gotClient(self):
        self.build_trees = False
        self.trunk_height = 5, 9
        self.fanout = 2, 4
    
    def newWorld(self, world):
        "Hook to reset dynamiting abilities in new worlds if not op."
        if not self.client.isBuilderPlus():
            self.build_trees = False
    
    def blockChanged(self, x, y, z, block, selected_block, fromloc):
        "Hook trigger for block changes."
        tobuild = []
        # Randomise the variables
        trunk_height = random.randint(*self.trunk_height)
        fanout = random.randint(*self.fanout)
        if self.build_trees and block == BLOCK_PLANT:
            # Build the main tree bit
            for i in range(-fanout-1, fanout):
                for j in range(-fanout-1, fanout):
                    for k in range(-fanout-1, fanout):
                        if not self.client.AllowedToBuild(x+i, y+j, z+k):
                            return
                        if (i**2 + j**2 + k**2)**0.5 < fanout:
                            tobuild.append((i, j+trunk_height, k, BLOCK_LEAVES))
            # Build the trunk
            for i in range(trunk_height):
                tobuild.append((0, i, 0, BLOCK_LOG))
            # OK, send the build changes
            for dx, dy, dz, block in tobuild:
                try:
                    self.client.world[x+dx, y+dy, z+dz] = chr(block)
                    self.client.sendBlock(x+dx, y+dy, z+dz, block)
                    self.client.factory.queue.put((self.client, TASK_BLOCKSET, (x+dx, y+dy, z+dz, block)))
                except AssertionError:
                    pass
            return True

    @build_list
    @builder_only
    def commandBThreeB(self, parts, fromloc, overriderank):
        "/b3b blockname blockname2 blockname3 [x y z x2 y2 z2] - Builder\nSets all blocks in this area to block, checkered(3)."
        if len(parts) < 10 and len(parts) != 4:
            self.client.sendServerMessage("Please enter three types (and possibly two coord triples)")
        else:
            # Try getting block3 as a direct integer type.
            try:
                block3 = chr(int(parts[3]))
            except ValueError:
                # OK, try a symbolic type.
                try:
                    block2 = chr(globals()['BLOCK_%s' % parts[3].upper()])
                except KeyError:
                    self.client.sendErrorMessage("'%s' is not a valid block type." % parts[3])
                    return
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
            if len(parts) == 4:
                try:
                    x, y, z = self.client.last_block_changes[0]
                    x2, y2, z2 = self.client.last_block_changes[1]
                except IndexError:
                    self.client.sendServerMessage("You have not clicked two corners yet.")
                    return
            else:
                try:
                    x = int(parts[4])
                    y = int(parts[5])
                    z = int(parts[6])
                    x2 = int(parts[7])
                    y2 = int(parts[8])
                    z2 = int(parts[9])
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
                self.client.sendErrorMessage("Sorry, that area is too big for you to b3b.")
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
                                if (i+j+k)%3 == 0:
                                    curNewBlock = block3
                                elif (i+j+k)%2 == 0:
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
                    self.client.sendErrorMessage("Out of bounds b3b error.")
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
                        self.client.sendServerMessage("Your b3b just completed.")
                    pass
            do_step()

    @build_list
    @op_only
    @on_off_command
    def commandTree(self, onoff, fromloc, overriderank):
        "/tree on|off - Builder\nBuilds trees, save the earth!"
        if onoff == "on":
            self.build_trees = True
            self.client.sendServerMessage("You are now building trees; place a plant!")
        else:
            self.build_trees = False
            self.client.sendServerMessage("You are no longer building trees.")
    
    @build_list
    @op_only
    def commandDune(self, parts, fromloc, overriderank):
        "/dune - Op\nCreates a sand dune between the two blocks you touched last."
        # Use the last two block places
        try:
            x, y, z = self.client.last_block_changes[0]
            x2, y2, z2 = self.client.last_block_changes[1]
        except IndexError:
            self.client.sendServerMessage("You have not clicked two corners yet.")
            return
        if x > x2:
            x, x2 = x2, x
        if y > y2:
            y, y2 = y2, y
        if z > z2:
            z, z2 = z2, z
        x_range = x2 - x
        z_range = z2 - z
        # Draw all the blocks on, I guess
        # We use a generator so we can slowly release the blocks
        # We also keep world as a local so they can't change worlds and affect the new one
        world = self.client.world
        def generate_changes():
            for i in range(x, x2+1):
                for k in range(z, z2+1):
                    # Work out the height at this place
                    dx = (x_range / 2.0) - abs((x_range / 2.0) - (i - x))
                    dz = (z_range / 2.0) - abs((z_range / 2.0) - (k - z))
                    dy = int((dx**2 * dz**2) ** 0.2)
                    for j in range(y, y+dy+1):
                        if not self.client.AllowedToBuild(i, j, k) and not overriderank:
                            return
                        block = BLOCK_SAND if j == y+dy else BLOCK_SAND
                        try:
                            world[i, j, k] = chr(block)
                        except AssertionError:
                            pass
                        self.client.queueTask(TASK_BLOCKSET, (i, j, k, block), world=world)
                        self.client.sendBlock(i, j, k, block)
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
                if fromloc == "user":
                    self.client.sendServerMessage("Your dune just completed.")
                pass
        do_step()

    @build_list
    @op_only
    def commandHill(self, parts, fromloc, overriderank):
        "/hill - Op\nCreates a hill between the two blocks you touched last."
        # Use the last two block places
        try:
            x, y, z = self.client.last_block_changes[0]
            x2, y2, z2 = self.client.last_block_changes[1]
        except IndexError:
            self.client.sendServerMessage("You have not clicked two corners yet.")
            return
        if x > x2:
            x, x2 = x2, x
        if y > y2:
            y, y2 = y2, y
        if z > z2:
            z, z2 = z2, z
        x_range = x2 - x
        z_range = z2 - z
        # Draw all the blocks on, I guess
        # We use a generator so we can slowly release the blocks
        # We also keep world as a local so they can't change worlds and affect the new one
        world = self.client.world
        def generate_changes():
            for i in range(x, x2+1):
                for k in range(z, z2+1):
                    # Work out the height at this place
                    dx = (x_range / 2.0) - abs((x_range / 2.0) - (i - x))
                    dz = (z_range / 2.0) - abs((z_range / 2.0) - (k - z))
                    dy = int((dx**2 * dz**2) ** 0.2)
                    for j in range(y, y+dy+1):
                        if not self.client.AllowedToBuild(x, y, z) and not overriderank:
                            return
                        block = BLOCK_GRASS if j == y+dy else BLOCK_DIRT
                        try:
                            world[i, j, k] = chr(block)
                        except AssertionError:
                            pass
                        self.client.queueTask(TASK_BLOCKSET, (i, j, k, block), world=world)
                        self.client.sendBlock(i, j, k, block)
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
                if fromloc == "user":
                    self.client.sendServerMessage("Your hill just completed.")
                pass
        do_step()

    @build_list
    @op_only
    def commandHole(self, parts, fromloc, overriderank):
        "/hole - Op\ncreates a hole between two blocks"
        # Use the last two block places
        try:
            x1, y1, z1 = self.client.last_block_changes[0]
            x2, y2, z2 = self.client.last_block_changes[1]
        except IndexError:
                self.client.sendServerMessage("You have not clicked two corners yet")
                return
        if x1 > x2:
            x1, x2 = x2, x1
        if y1 > y2:
            y1, y2 = y2, y1
        if z1 > z2:
            z1, z2 = z2, z1
        x_range = x2 - x1
        z_range = z2 - z1
        block = BLOCK_AIR
        world = self.client.world
        def generate_changes():
            for x in range(x1, x2+1):
                for z in range(z1, z2+1):
                    # Work out the height at this place
                    dx = (x_range / 2.0) - abs((x_range / 2.0) - (x - x1))
                    dz = (z_range / 2.0) - abs((z_range / 2.0) - (z - z1))
                    dy = int((dx**2 * dz**2) ** 0.3)
                    for y in range(y1-dy-1, y1+1):
                        if not self.client.AllowedToBuild(x, y, z) and not overriderank:
                            return
                        if y < 0:
                            continue
                        try:
                            world[x, y, z] = chr(block)
                        except AssertionError:
                            pass
                        self.client.queueTask(TASK_BLOCKSET, (x, y, z, block), world = world)
                        self.client.sendBlock(x, y, z, block)
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
                if fromloc == "user":
                    self.client.sendServerMessage("Your hole just completed.")
                pass
        do_step()

    @build_list
    @op_only
    def commandLake(self, parts, fromloc, overriderank):
        "/lake - Op\ncreates a lake between two blocks"
        # Use the last two block places
        try:
            x1, y1, z1 = self.client.last_block_changes[0]
            x2, y2, z2 = self.client.last_block_changes[1]
        except IndexError:
                self.client.sendServerMessage("You have not clicked two corners yet")
                return
        if x1 > x2:
            x1, x2 = x2, x1
        if y1 > y2:
            y1, y2 = y2, y1
        if z1 > z2:
            z1, z2 = z2, z1
        x_range = x2 - x1
        z_range = z2 - z1
        block = BLOCK_WATER
        world = self.client.world
        def generate_changes():
            for x in range(x1, x2+1):
                for z in range(z1, z2+1):
                    # Work out the height at this place
                    dx = (x_range / 2.0) - abs((x_range / 2.0) - (x - x1))
                    dz = (z_range / 2.0) - abs((z_range / 2.0) - (z - z1))
                    dy = int((dx**2 * dz**2) ** 0.3)
                    for y in range(y1-dy-1, y1):
                        if not self.client.AllowedToBuild(x, y, z) and not overriderank:
                            return
                        try:
                            world[x, y, z] = chr(block)
                        except AssertionError:
                            pass
                        self.client.queueTask(TASK_BLOCKSET, (x, y, z, block), world = world)
                        self.client.sendBlock(x, y, z, block)
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
                if fromloc == "user":
                    self.client.sendServerMessage("Your lake just completed.")
                pass
        do_step()

    @build_list
    @op_only
    def commandMountain(self, parts, fromloc, overriderank):
        "/mountain blockname - Op\nCreates a mountain between the two blocks you touched last."
        if len(parts) < 8 and len(parts) != 2:
            self.client.sendServerMessage("Please enter a type.")
            return
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
        x_range = x2 - x
        z_range = z2 - z
        # Draw all the blocks on, I guess
        # We use a generator so we can slowly release the blocks
        # We also keep world as a local so they can't change worlds and affect the new one
        world = self.client.world
        def generate_changes():
            for i in range(x, x2+1):
                for k in range(z, z2+1):
                    # Work out the height at this place
                    dx = (x_range / 2.0) - abs((x_range / 2.0) - (i - x))
                    dz = (z_range / 2.0) - abs((z_range / 2.0) - (k - z))
                    dy = int((dx**2 * dz**2) ** 0.3)
                    for j in range(y, y+dy+1):
                        if not self.client.AllowedToBuild(i, j, k) and not overriderank:
                            return
                        try:
                            world[i, j, k] = block
                        except AssertionError:
                            pass
                        self.client.queueTask(TASK_BLOCKSET, (i, j, k, block), world=world)
                        self.client.sendBlock(i, j, k, block)
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
                if fromloc == "user":
                    self.client.sendServerMessage("Your mountain just completed.")
                pass
        do_step()

    @build_list
    @op_only
    def commandPit(self, parts, fromloc, overriderank):
        "/pit - Op\ncreates a lava pit between two blocks"
        # Use the last two block places
        try:
            x1, y1, z1 = self.client.last_block_changes[0]
            x2, y2, z2 = self.client.last_block_changes[1]
        except IndexError:
                self.client.sendServerMessage("You have not clicked two corners yet")
                return
        if x1 > x2:
            x1, x2 = x2, x1
        if y1 > y2:
            y1, y2 = y2, y1
        if z1 > z2:
            z1, z2 = z2, z1
        x_range = x2 - x1
        z_range = z2 - z1
        block = BLOCK_LAVA
        world = self.client.world
        def generate_changes():
            for x in range(x1, x2+1):
                for z in range(z1, z2+1):
                    # Work out the height at this place
                    dx = (x_range / 2.0) - abs((x_range / 2.0) - (x - x1))
                    dz = (z_range / 2.0) - abs((z_range / 2.0) - (z - z1))
                    dy = int((dx**2 * dz**2) ** 0.3)
                    for y in range(y1-dy-1, y1):
                        if not self.client.AllowedToBuild(x, y, z) and not overriderank:
                            return
                        try:
                            world[x, y, z] = chr(block)
                        except AssertionError:
                            pass
                        self.client.queueTask(TASK_BLOCKSET, (x, y, z, block), world = world)
                        self.client.sendBlock(x, y, z, block)
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
                if fromloc == "user":
                    self.client.sendServerMessage("Your pit just completed.")
                pass
        do_step()

    @builder_only
    def commandReplaceNear(self, parts, byuser, overriderank):
        "/replacenear <radius> <blocktoreplace> <blockreplacing> - Builder\nAliases: /rn\nReplaces blocks within a radius of your position."
        if len(parts) < 3:
            self.client.sendServerMessage("Please enter three parameters.")
        else:
            try:
                size = int(parts[1])
            except ValueError:
                self.client.sendServerMessage("Size must be a Number.")
                return
            blockA = self.client.GetBlockValue(parts[2])
            if blockA == None:
                return
            blockB = self.client.GetBlockValue(parts[3])
            if blockB == None:
                return
            if len(parts) == 4:
                try:
                    x, y, z = self.client.x>>5, self.client.y>>5, self.client.z>>5
                except IndexError:
                    self.client.sendServerMessage("You have not clicked a block yet.")
                    return
            else:
                # Get the player's current position
                x, y, z = self.client.x>>5, self.client.y>>5, self.client.z>>5
            if self.client.isDirectorPlus() or overriderank:
                limit = self.client.factory.build_director
            elif self.client.isAdmin() or self.client.isCoder():
                limit = self.client.factory.build_admin
            elif self.client.isMod():
                limit = self.client.factory.build_mod
            elif self.client.isOp() or self.client.isWorldOwner():
                limit = self.client.factory.build_op
            else:
                limit = self.client.factory.build_other
            if size > limit:
                self.client.sendErrorMessage("Sorry, that area is too big for you to replacenear.")
                return
            # Keep the building in the current world
            world = self.client.world
            # Draw the blocks on
            def generate_changes():
                for i in range(x-size, x+size):
                    for j in range(y-size, y+size):
                        for k in range(z-size, z+size):
                            if not self.client.AllowedToBuild(i, j, k) and not overriderank:
                                return
                            try:
                                check_offset = world.blockstore.get_offset(i, j, k)
                                block = world.blockstore.raw_blocks[check_offset]
                                if block == blockA:
                                    world[i, j, k] = blockB
                                    self.client.runHook("blockchange", x, y, z, ord(block), ord(block), byuser)
                                    self.client.queueTask(TASK_BLOCKSET, (i, j, k, blockB), world=world)
                                    self.client.sendBlock(i, j, k, blockB)
                            except AssertionError:
                                self.client.sendErrorMessage("Out of bounds replacenear error.")
                                return
                            yield
            block_iter = iter(generate_changes())
            def do_step():
                # Do 10 blocks
                try:
                    for x in range(10):
                        block_iter.next()
                    reactor.callLater(0.01, do_step)
                except StopIteration:
                    if byuser:
                        self.client.sendServerMessage("Your replacenear just completed.")
                    pass
            do_step()

    @build_list
    @builder_only
    def commandBrep(self, parts, fromloc, overriderank):
        "/replace blockA blockB [x y z x2 y2 z2] - Builder\nAliases: brep\nReplaces all blocks of blockA in this area to blockB."
        if len(parts) < 9 and len(parts) != 3:
            self.client.sendServerMessage("Please enter types (and possibly two coord triples)")
        else:
            blockA = self.client.GetBlockValue(parts[1])
            blockB = self.client.GetBlockValue(parts[2])
            if blockA == None or blockB == None:
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
                self.client.sendServerMessage("Sorry, that area is too big for you to replace.")
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
                                if not self.client.AllowedToBuild(i, j, k) and fromloc != "user":
                                    return
                                check_offset = world.blockstore.get_offset(i, j, k)
                                block = world.blockstore.raw_blocks[check_offset]
                                if block == blockA:
                                    world[i, j, k] = blockB
                                    self.client.runHook("blockchange", x, y, z, ord(block), ord(block), fromloc)
                                    self.client.queueTask(TASK_BLOCKSET, (i, j, k, blockB), world=world)
                                    self.client.sendBlock(i, j, k, blockB)
                                    yield
                except AssertionError:
                    self.client.sendServerMessage("Out of bounds replace error.")
                    return
            # Now, set up a loop delayed by the reactor
            block_iter = iter(generate_changes())
            def do_step():
                # Do 10 blocks
                try:
                    for x in range(10):
                        block_iter.next()
                    reactor.callLater(0.01, do_step)
                except StopIteration:
                    if fromloc == "user":
                        self.client.sendServerMessage("Your replace just completed.")
                    pass
            do_step()

    @build_list
    @op_only
    def commandCreplace(self, parts, fromloc, overriderank):
        "/creplace typeA typeB typeC [x y z x2 y2 z2] - Op\nAliases: crep\nReplaces all blocks of typeA in this cuboid to typeB and typeC."
        if len(parts) < 10 and len(parts) != 4:
            self.client.sendServerMessage("Please enter the type to replace and two other types")
            self.client.sendServerMessage("(and possibly two coord triples)")
        else:
            blockA = self.client.GetBlockValue(parts[1])
            blockB = self.client.GetBlockValue(parts[2])
            blockC = self.client.GetBlockValue(parts[3])
            if blockA == None or blockB == None or blockC == None:
                return            
            # If they only provided the type argument, use the last two block places
            if len(parts) == 4:
                try:
                    x, y, z = self.client.last_block_changes[0]
                    x2, y2, z2 = self.client.last_block_changes[1]
                except IndexError:
                    self.client.sendServerMessage("You have not clicked two corners yet.")
                    return
            else:
                try:
                    x = int(parts[4])
                    y = int(parts[5])
                    z = int(parts[6])
                    x2 = int(parts[7])
                    y2 = int(parts[8])
                    z2 = int(parts[9])
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
                self.client.sendServerMessage("Sorry, that area is too big for you to rep.")
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
                                blockcheck = world.blockstore.raw_blocks[world.blockstore.get_offset(i, j, k)]
                                if blockcheck == blockA:
                                    if (i + j + k) % 2 == 0:
                                        var_block = blockB
                                    else:
                                        var_block = blockC
                                    world[i, j, k] = var_block
                                    self.client.queueTask(TASK_BLOCKSET, (i, j, k, var_block), world=world)
                                    self.client.sendBlock(i, j, k, var_block)
                                    yield
                except AssertionError:
                    self.client.sendServerMessage("Out of bounds creplace error.")
                    return
            # Now, set up a loop delayed by the reactor
            block_iter = iter(generate_changes())
            def do_step():
                # Do 10 blocks
                try:
                    for x in range(10):
                        block_iter.next()
                    reactor.callLater(0.01, do_step)
                except StopIteration:
                    if fromloc == "user":
                        self.client.sendServerMessage("Your creplace just completed.")
                    pass
            do_step()

    @build_list
    @op_only
    def commandFill(self, parts, fromloc, overriderank):
        "/fill blockname repblock [x y z x2 y2 z2] - Op\nFills the area with the block."
        if len(parts) < 9 and len(parts) != 3:
            self.client.sendSplitServerMessage("Please enter a type and a type to replace (and possibly two coord triples)")
            self.client.sendSplitServerMessage("Note that you must place two blocks to use it. The first block sets where to spread from and the second block sets which directions to spread.")
        else:
            blockA = self.client.GetBlockValue(parts[1])
            blockB = self.client.GetBlockValue(parts[2])
            if blockA == None or blockB == None:
                return
            # If they only provided the type argument, use the last block place
            if len(parts) == 3:
                try:
                    x, y, z = self.client.last_block_changes[1]
                    x2, y2, z2 = self.client.last_block_changes[0]
                except IndexError:
                    self.client.sendServerMessage("You have not clicked two points yet.")
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
            limit = self.getBuildLimit(overriderank)
            var_locxchecklist = [(1, 0, 0), (-1, 0, 0)]
            var_locychecklist = [(0, 1, 0), (0, -1, 0)]
            var_loczchecklist = [(0, 0, 1), (0 ,0, -1)]
            var_locchecklist = []
            if x != x2:
                var_locchecklist = var_locchecklist + var_locxchecklist
            if y != y2:
                var_locchecklist = var_locchecklist + var_locychecklist
            if z != z2:
                var_locchecklist = var_locchecklist + var_loczchecklist
            if var_locchecklist == []:
                self.client.sendServerMessage("Repeated points error.")
                return
            self.var_blocklist = [(x, y, z, (-20, -20, -20))]
            # Draw all the blocks on, I guess
            # We use a generator so we can slowly release the blocks
            # We also keep world as a local so they can't change worlds and affect the new one
            world = self.client.world
            try:
                if not self.client.AllowedToBuild(x, y, z):
                    self.client.sendServerMessage("You do not have permission to build here.")
                    return
                world[x, y, z] = blockA
                self.client.queueTask(TASK_BLOCKSET, (x, y, z, blockA), world=world)
                self.client.sendBlock(x, y, z, block)
            except:
                pass
            def generate_changes():
                var_blockchanges = 0
                while self.var_blocklist != []:
                    if var_blockchanges > limit:
                        self.client.sendServerMessage("You have exceeded the fill limit for your rank.")
                        return
                    i, j, k, positionprevious = self.var_blocklist[0]
                    var_blockchanges += 1
                    for offsettuple in var_locchecklist:
                        ia, ja, ka = offsettuple
                        ri, rj, rk = i + ia, j + ja, k + ka
                        if (ri, rj, rk) != positionprevious:
                            try:
                                if not self.client.AllowedToBuild(ri, rj, rk) and not overriderank:
                                    self.client.sendServerMessage("You do not have permission to build here.")
                                    return
                                checkblock = world.blockstore.raw_blocks[world.blockstore.get_offset(ri, rj, rk)]
                                if checkblock == blockB:
                                    world[ri, rj, rk] = blockA
                                    self.client.queueTask(TASK_BLOCKSET, (ri, rj, rk, blockA), world=world)
                                    self.client.sendBlock(ri, rj, rk, blockA)
                                    self.var_blocklist.append((ri, rj, rk,(i,j,k)))
                            except AssertionError:
                                pass
                            yield
                    del self.var_blocklist[0]
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
                        self.client.sendServerMessage("Your fill just completed.")
                    pass
            do_step()

    @build_list
    @builder_only
    def commandStairs(self, parts, fromloc, overriderank):
        "/stairs blockname height [c] [x y z x2 y2 z2] - Builder\nc = counter-clockwise\nBuilds a spiral staircase."
        if len(parts) < 9 and len(parts) != 3 and len(parts) != 4:
            self.client.sendServerMessage("Please enter a blocktype height (c (for counter-clockwise)")
            self.client.sendServerMessage("(and possibly two coord triples)")
            self.client.sendServerMessage("If the two points are on the 'ground' adjacent to each other, then")
            self.client.sendServerMessage("the second point will spawn the staircase and the first will")
            self.client.sendServerMessage("be used for the initial orientation")
        else:
            # Try getting the counter-clockwise flag
            if len(parts) == 4:
                if parts[3] == 'c':
                    counterflag = 1
                else:
                    self.client.sendServerMessage("The third entry must be 'c' for counter-clockwise")
                    return
            else:
                counterflag = -1
            # Try getting the height as a direct integer type.
            try:
                height = int(parts[2])
            except ValueError:
                self.client.sendServerMessage("The height must be an integer")
                return
            # Try getting the block as a direct integer type.
            try:
                block = chr(int(parts[1]))
            except ValueError:
                # OK, try a symbolic type.
                try:
                    block = chr(globals()['BLOCK_%s' % parts[1].upper()])
                except KeyError:
                    self.client.sendServerMessage("'%s' is not a valid block type." % parts[1])
                    return
            # Check the block is valid
            if ord(block) > 49:
                self.client.sendServerMessage("'%s' is not a valid block type." % parts[1])
                return
            op_blocks = [BLOCK_SOLID, BLOCK_WATER, BLOCK_LAVA]
            if ord(block) in op_blocks and not self.client.isOpPlus():
                self.client.sendServerMessage("Sorry, but you can't use that block.")
                return
            # If they only provided the type argument, use the last two block places
            if len(parts) == 3 or len(parts) == 4:
                try:
                    x, y, z = self.client.last_block_changes[0]
                    x2, y2, z2 = self.client.last_block_changes[1]
                except IndexError:
                    self.client.sendServerMessage("You have not clicked two corners yet.")
                    return
            else:
                if len(parts) == 9:
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
            if self.client.isDirectorPlus() or overriderank:
                limit = self.client.factory.build_director
            elif self.client.isAdmin() or self.client.isCoder():
                limit = self.client.factory.build_admin
            elif self.client.isMod():
                limit = self.client.factory.build_mod
            elif self.client.isOp() or self.client.isWorldOwner():
                limit = self.client.factory.build_op
            else:
                limit = self.client.factory.build_other
            # Stop them doing silly things
            if height * 4 > limit:
                self.client.sendServerMessage("Sorry, that area is too big for you to make stairs.")
                return
            # Draw all the blocks on, I guess
            # We use a generator so we can slowly release the blocks
            # We also keep world as a local so they can't change worlds and affect the new one
            world = self.client.world
            def generate_changes():
                if abs(x-x2)+abs(z-z2) == 1:
                    if x - x2 == -1:
                        orientation = 1
                    elif z - z2 == -1:
                        orientation = 2
                    elif x - x2 == 1:
                        orientation = 3
                    else:
                        orientation = 4
                else:
                    orientation = 1
                if height >= 0:
                    heightsign = 1
                else:
                    heightsign = -1
                stepblock = chr(BLOCK_STEP)
                for h in range(abs(height)):
                    locy = y+h*heightsign
                    if counterflag == -1:
                        if orientation == 1:
                            blocklist = [(x,locy,z),(x+1,locy,z+1),(x+1,locy,z),(x+1,locy,z-1)]
                        elif orientation == 2:
                            blocklist = [(x,locy,z),(x-1,locy,z+1),(x,locy,z+1),(x+1,locy,z+1)]
                        elif orientation == 3:
                            blocklist = [(x,locy,z),(x-1,locy,z-1),(x-1,locy,z),(x-1,locy,z+1)]
                        else:
                            blocklist = [(x,locy,z),(x+1,locy,z-1),(x,locy,z-1),(x-1,locy,z-1)]
                    else:
                        if orientation == 1:
                            blocklist = [(x,locy,z),(x+1,locy,z-1),(x+1,locy,z),(x+1,locy,z+1)]
                        elif orientation == 2:
                            blocklist = [(x,locy,z),(x+1,locy,z+1),(x,locy,z+1),(x-1,locy,z+1)]
                        elif orientation == 3:
                            blocklist = [(x,locy,z),(x-1,locy,z+1),(x-1,locy,z),(x-1,locy,z-1)]
                        else:
                            blocklist = [(x,locy,z),(x-1,locy,z-1),(x,locy,z-1),(x+1,locy,z-1)]
                    orientation = orientation - heightsign*counterflag
                    if orientation > 4:
                        orientation = 1
                    if orientation < 1:
                        orientation = 4
                    for entry in blocklist:
                        i,j,k = entry
                        if not self.client.AllowedToBuild(i, j, k):
                            return
                    for entry in blocklist[:3]:
                        i,j,k = entry
                        try:
                            world[i, j, k] = block
                        except AssertionError:
                            self.client.sendServerMessage("Out of bounds stairs error.")
                            return
                        self.client.queueTask(TASK_BLOCKSET, (i, j, k, block), world=world)
                        self.client.sendBlock(i, j, k, block)
                        yield
                        i,j,k = blocklist[3]
                        try:
                            world[i, j, k] = stepblock
                        except AssertionError:
                            self.client.sendServerMessage("Out of bounds stairs error.")
                            return
                        self.client.queueTask(TASK_BLOCKSET, (i, j, k, stepblock), world=world)
                        self.client.sendBlock(i, j, k, stepblock)
                        yield
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
                        self.client.sendServerMessage("Your stairs just completed.")
                    pass
            do_step()

    @build_list
    @builder_only
    def commandSphere(self, parts, fromloc, overriderank):
        "/sphere blocktype radius [x y z] - Builder\nPlace/delete a block and /sphere block radius"
        if len(parts) < 6 and len(parts) != 3:
            self.client.sendServerMessage("Please enter a type (and possibly two coord triples)")
        else:
            # Try getting the radius
            try:
                radius = int(parts[2])
            except ValueError:
                self.client.sendServerMessage("Radius must be a Number.")
                return
            block = self.client.GetBlockValue(parts[1])
            if block == None:
                return
            # If they only provided the type argument, use the last two block places
            if len(parts) == 3:
                try:
                    x, y, z = self.client.last_block_changes[0]
                except IndexError:
                    self.client.sendServerMessage("You have not clicked for a center yet.")
                    return
            else:
                try:
                    x = int(parts[3])
                    y = int(parts[4])
                    z = int(parts[5])
                except ValueError:
                    self.client.sendServerMessage("All coordinate parameters must be integers.")
                    return
            limit = self.getBuildLimit(overriderank)
            if (radius*2)**3>limit:
                return
            # Draw all the blocks on, I guess
            # We use a generator so we can slowly release the blocks
            # We also keep world as a local so they can't change worlds and affect the new one
            world = self.client.world
            def generate_changes():
                for i in range(-radius-1, radius):
                    for j in range(-radius-1, radius):
                        for k in range(-radius-1, radius):
                            if (i**2 + j**2 + k**2)**0.5 < radius:
                                if not self.client.AllowedToBuild(x+i, y+j, z+k):
                                    return
                                try:
                                    world[x+i, y+j, z+k] = block
                                except AssertionError:
                                    self.client.sendServerMessage("Out of bounds sphere error.")
                                    return
                                self.client.queueTask(TASK_BLOCKSET, (x+i, y+j, z+k, block), world=world)
                                self.client.sendBlock(x+i, y+j, z+k, block)
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
                    if fromloc == "user":
                        self.client.sendServerMessage("Your sphere just completed.")
                    pass
            do_step()

    @build_list
    @builder_only
    def commandHSphere(self, parts, fromloc, overriderank):
        "/hsphere blocktype radius [x y z] - Builder\nPlace/delete a block, makes a hollow /sphere"
        if len(parts) < 6 and len(parts) != 3:
            self.client.sendServerMessage("Please enter a type (and possibly two coord triples)")
        else:
            # Try getting the radius
            try:
                radius = int(parts[2])
            except ValueError:
                self.client.sendServerMessage("Radius must be a Number.")
                return
            block = self.client.GetBlockValue(parts[1])
            if block == None:
                return
            # If they only provided the type argument, use the last two block places
            if len(parts) == 3:
                try:
                    x, y, z = self.client.last_block_changes[0]
                except IndexError:
                    self.client.sendServerMessage("You have not clicked for a center yet.")
                    return
            else:
                try:
                    x = int(parts[3])
                    y = int(parts[4])
                    z = int(parts[5])
                except ValueError:
                    self.client.sendServerMessage("All coordinate parameters must be integers.")
                    return
            limit = self.getBuildLimit(overriderank)
            if (radius*2)**3>limit:
                return
            # Draw all the blocks on, I guess
            # We use a generator so we can slowly release the blocks
            # We also keep world as a local so they can't change worlds and affect the new one
            world = self.client.world
            def generate_changes():
                for i in range(-radius-1, radius):
                    for j in range(-radius-1, radius):
                        for k in range(-radius-1, radius):
                            if (i**2 + j**2 + k**2)**0.5 < radius and (i**2 + j**2 + k**2)**0.5 > radius-1.49:
                                if not self.client.AllowedToBuild(x+i, y+j, z+k) and not permissionoverride:
                                    return
                                try:
                                    world[x+i, y+j, z+k] = block
                                except AssertionError:
                                    self.client.sendServerMessage("Out of bounds sphere error.")
                                    return
                                self.client.queueTask(TASK_BLOCKSET, (x+i, y+j, z+k, block), world=world)
                                self.client.sendBlock(x+i, y+j, z+k, block)
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
                    if fromloc == "user":    
                        self.client.sendServerMessage("Your hsphere just completed.")
                    pass
            do_step()

    @build_list
    @builder_only
    def commandCurve(self, parts, fromloc, overriderank):
        "/curve blockname [x y z x2 y2 z2 x3 y3 z3] - Builder\nSets a line of blocks along three points to block."
        if len(parts) < 11 and len(parts) != 2:
            self.client.sendServerMessage("Please enter a type (and possibly three coord triples)")
        else:
            # Try getting the block as a direct integer type.
            try:
                block = chr(int(parts[1]))
            except ValueError:
                # OK, try a symbolic type.
                try:
                    block = chr(globals()['BLOCK_%s' % parts[1].upper()])
                except KeyError:
                    self.client.sendServerMessage("'%s' is not a valid block type." % parts[1])
                    return
            # Check the block is valid
            if ord(block) > 49:
                self.client.sendServerMessage("'%s' is not a valid block type." % parts[1])
                return
            op_blocks = [BLOCK_SOLID, BLOCK_WATER, BLOCK_LAVA]
            if ord(block) in op_blocks and not self.client.isOpPlus():
                self.client.sendServerMessage("Sorry, but you can't use that block.")
                return
            # If they only provided the type argument, use the last two block places
            if len(parts) == 2:
                try:
                    x, y, z = self.client.last_block_changes[0]
                    x2, y2, z2 = self.client.last_block_changes[1]
                    x3, y3, z3 = self.client.last_block_changes[2]
                except:
                    self.client.sendServerMessage("You have not clicked 3 points yet.")
                    return
            else:
                try:
                    x = int(parts[2])
                    y = int(parts[3])
                    z = int(parts[4])
                    x2 = int(parts[5])
                    y2 = int(parts[6])
                    z2 = int(parts[7])
                    x3 = int(parts[8])
                    y3 = int(parts[9])
                    z3 = int(parts[10])
                except ValueError:
                    self.client.sendServerMessage("All coordinate parameters must be integers.")
                    return
            limit = self.getBuildLimit(overriderank)
            # Stop them doing silly things
            if 2*((x-x2)**2+(y-y2)**2+(z-z2)**2)**0.5+2*((x2-x3)**2+(y2-y3)**2+(z2-z3)**2)**0.5 > limit:
                self.client.sendServerMessage("Sorry, that area is too big for you to curve.")
                return
            # Draw all the blocks on, I guess
            # We use a generator so we can slowly release the blocks
            # We also keep world as a local so they can't change worlds and affect the new one
            world = self.client.world
            def generate_changes():                
                # curve list
                steps1 = float(2*((x3-x)**2+(y3-y)**2+(z3-z)**2)**0.5)
                steps2 = float(2*((x2-x3)**2+(y2-y3)**2+(z2-z3)**2)**0.5) + steps1
                coordinatelist = []
                for i in range(steps2+1):
                    t = float(i)
                    var_x = (x3-x)*((t)/(steps1) * (t-steps2)/(steps1-steps2)) + (x2-x)*((t)/(steps2) * (t-steps1)/(steps2-steps1))
                    var_y = (y3-y)*((t)/(steps1) * (t-steps2)/(steps1-steps2)) + (y2-y)*((t)/(steps2) * (t-steps1)/(steps2-steps1))
                    var_z = (z3-z)*((t)/(steps1) * (t-steps2)/(steps1-steps2)) + (z2-z)*((t)/(steps2) * (t-steps1)/(steps2-steps1))
                    coordinatelist.append((int(var_x)+x,int(var_y)+y,int(var_z)+z))
                finalcoordinatelist = []
                finalcoordinatelist = [coordtuple for coordtuple in coordinatelist if coordtuple not in finalcoordinatelist]
                for coordtuple in finalcoordinatelist:
                    i = coordtuple[0]
                    j = coordtuple[1]
                    k = coordtuple[2]
                    if not self.client.AllowedToBuild(i, j, k):
                        return
                    try:
                        world[i, j, k] = block
                    except AssertionError:
                        self.client.sendServerMessage("Out of bounds curve error.")
                        return
                    self.client.queueTask(TASK_BLOCKSET, (i, j, k, block), world=world)
                    self.client.sendBlock(i, j, k, block)
                    yield
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
                        self.client.sendServerMessage("Your curve just completed.")
                    pass
            do_step()

    @build_list
    @op_only
    def commandPyramid(self, parts, fromloc, overriderank):
        "/pyramid blockname height fill [x y z] - Op\nSets all blocks in this area to be a pyramid."
        if len(parts) < 7 and len(parts) != 4:
            self.client.sendServerMessage("Please enter a block type height and fill?")
        else:
            # Try getting the fill
            fill = parts[3]
            if fill=='true' or fill=='false':
                pass
            else:
                self.client.sendServerMessage("fill must be true or false")
                return
            # Try getting the height
            try:
                height = int(parts[2])
            except ValueError:
                self.client.sendServerMessage("Height must be a Number.")
                return
            # Try getting the block as a direct integer type.
            try:
                block = chr(int(parts[1]))
            except ValueError:
                # OK, try a symbolic type.
                try:
                    block = chr(globals()['BLOCK_%s' % parts[1].upper()])
                except KeyError:
                    self.client.sendServerMessage("'%s' is not a valid block type." % parts[1])
                    return
            # Check the block is valid
            if ord(block) > 49:
                self.client.sendServerMessage("'%s' is not a valid block type." % parts[1])
                return
            op_blocks = [BLOCK_SOLID, BLOCK_WATER, BLOCK_LAVA]
            if ord(block) in op_blocks and not self.client.isOpPlus():
                self.client.sendServerMessage("Sorry, but you can't use that block.")
                return
            # If they only provided the type argument, use the last two block places
            if len(parts) == 4:
                try:
                    x, y, z = self.client.last_block_changes[0]
                except IndexError:
                    self.client.sendServerMessage("You have not clicked two corners yet.")
                    return
            else:
                try:
                    x = int(parts[4])
                    y = int(parts[5])
                    z = int(parts[6])
                except ValueError:
                    self.client.sendServerMessage("All coordinate parameters must be integers.")
                    return
            pointlist = []
            for i in range(abs(height)):
                if height>0:
                    point1 = [x-i, y+height-i-1,z-i]
                    point2 = [x+i, y+height-i-1,z+i]
                else:
                    point1 = [x-i, y+height+i+1,z-i]
                    point2 = [x+i, y+height+i+1,z+i]
                pointlist = pointlist+[(point1,point2)]
            limit = self.getBuildLimit(overriderank)
            # Stop them doing silly things
            if (x) * (y) * (z)/2 > limit:
                self.client.sendServerMessage("Sorry, that area is too big for you to pyramid.")
                return
            # Draw all the blocks on, I guess
            # We use a generator so we can slowly release the blocks
            # We also keep world as a local so they can't change worlds and affect the new one
            world = self.client.world
            def generate_changes():
                for pointtouple in pointlist:
                    x,y,z = pointtouple[0]
                    x2,y2,z2 = pointtouple[1]
                    for i in range(x, x2+1):
                        for j in range(y, y2+1):
                            for k in range(z, z2+1):
                                if not self.client.AllowedToBuild(i, j, k) and not overriderank:
                                    return
                                if fill == 'true' or (i==x and j==y) or (i==x2 and j==y2) or (j==y2 and k==z2) or (i==x2 and k==z2) or (j==y and k==z) or (i==x and k==z) or (i==x and k==z2) or (j==y and k==z2) or (i==x2 and k==z) or (j==y2 and k==z) or (i==x and j==y2) or (i==x2 and j==y):
                                    try:
                                       world[i, j, k] = block
                                    except AssertionError:
                                        self.client.sendServerMessage("Out of bounds pyramid error.")
                                        return
                                    self.client.queueTask(TASK_BLOCKSET, (i, j, k, block), world=world)
                                    self.client.sendBlock(i, j, k, block)
                                    yield
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
                        self.client.sendServerMessage("Your pyramid just completed.")
                    pass
            do_step()

    @build_list
    @builder_only
    def commandLine(self, parts, fromloc, overriderank):
        "/line blockname [x y z x2 y2 z2] - Member\nSets all blocks between two points to be a line."
        if len(parts) < 8 and len(parts) != 2:
            self.client.sendServerMessage("Please enter a type (and possibly two coord triples)")
        else:
            # Try getting the block as a direct integer type.
            try:
                block = chr(int(parts[1]))
            except ValueError:
                # OK, try a symbolic type.
                try:
                    block = chr(globals()['BLOCK_%s' % parts[1].upper()])
                except KeyError:
                    self.client.sendServerMessage("'%s' is not a valid block type." % parts[1])
                    return
            # Check the block is valid
            if ord(block) > 49:
                self.client.sendServerMessage("'%s' is not a valid block type." % parts[1])
                return
            op_blocks = [BLOCK_SOLID, BLOCK_WATER, BLOCK_LAVA]
            if ord(block) in op_blocks and not self.client.isOpPlus():
                self.client.sendServerMessage("Sorry, but you can't use that block.")
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
            steps = int(((x2-x)**2+(y2-y)**2+(z2-z)**2)**0.5)
            if steps == 0:
                self.client.sendServerMessage("Your lines need to be longer.")
                return
            mx = float(x2-x)/steps
            my = float(y2-y)/steps
            mz = float(z2-z)/steps
            coordinatelist1 = []
            for t in range(steps+1):
                coordinatelist1.append((int(round(mx*t+x)),int(round(my*t+y)),int(round(mz*t+z))))
            coordinatelist2 = []
            coordinatelist2 = [coordtuple for coordtuple in coordinatelist1 if coordtuple not in coordinatelist2]
            limit = self.getBuildLimit(overriderank)
            # Stop them doing silly things
            if len(coordinatelist2) > limit:
                self.client.sendServerMessage("Sorry, that area is too big for you to line.")
                return
            # Draw all the blocks on, I guess
            # We use a generator so we can slowly release the blocks
            # We also keep world as a local so they can't change worlds and affect the new one
            world = self.client.world
            def generate_changes():
                for coordtuple in coordinatelist2:
                    i = coordtuple[0]
                    j = coordtuple[1]
                    k = coordtuple[2]
                    if not self.client.AllowedToBuild(i, j, k) and not overriderank:
                        return
                    try:
                        world[i, j, k] = block
                    except AssertionError:
                        self.client.sendServerMessage("Out of bounds line error.")
                        return
                    self.client.queueTask(TASK_BLOCKSET, (i, j, k, block), world=world)
                    self.client.sendBlock(i, j, k, block)
                    yield
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
                        self.client.sendServerMessage("Your line just completed.")
                    pass
            do_step()

    @build_list
    @op_only
    def commandCsphere(self, parts, fromloc, overriderank):
        "/csphere blocktype blocktype radius [x y z] - Op\nPlace/delete a block and /csphere block radius"
        if len(parts) < 7 and len(parts) != 4:
            self.client.sendServerMessage("Please enter two types a radius(and possibly a coord triple)")
        else:
            # Try getting the radius
            try:
                radius = int(parts[3])
            except ValueError:
                self.client.sendServerMessage("Radius must be a Number.")
                return
            # Try getting block2 as a direct integer type.
            try:
                block2 = chr(int(parts[2]))
            except ValueError:
                # OK, try a symbolic type.
                try:
                    block2 = chr(globals()['BLOCK_%s' % parts[2].upper()])
                except KeyError:
                    self.client.sendServerMessage("'%s' is not a valid block type." % parts[2])
                    return
            # Try getting the block as a direct integer type.
            try:
                block = chr(int(parts[1]))
            except ValueError:
                # OK, try a symbolic type.
                try:
                    block = chr(globals()['BLOCK_%s' % parts[1].upper()])
                except KeyError:
                    self.client.sendServerMessage("'%s' is not a valid block type." % parts[1])
                    return
            # Check the block is valid
            if ord(block) > 49:
                self.client.sendServerMessage("'%s' is not a valid block type." % parts[1])
                return
            # Check that block2 is valid
            if ord(block2) > 49:
                self.client.sendServerMessage("'%s' is not a valid block type." % parts[1])
                return
            # If they only provided the type argument, use the last two block places
            if len(parts) == 4:
                try:
                    x, y, z = self.client.last_block_changes[0]
                except IndexError:
                    self.client.sendServerMessage("You have not clicked for a center yet.")
                    return
            else:
                try:
                    x = int(parts[3])
                    y = int(parts[4])
                    z = int(parts[5])
                except ValueError:
                    self.client.sendServerMessage("All coordinate parameters must be integers.")
                    return
            limit = self.getBuildLimit(overriderank)
            if (radius*2)**3>limit:
                self.client.sendServerMessage("Sorry, that area is too big for you to csphere.")
                return
            # Draw all the blocks on, I guess
            # We use a generator so we can slowly release the blocks
            # We also keep world as a local so they can't change worlds and affect the new one
            world = self.client.world
            def generate_changes():
                ticker = 0
                for i in range(-radius-1, radius):
                    for j in range(-radius-1, radius):
                        for k in range(-radius-1, radius):
                            if (i**2 + j**2 + k**2)**0.5 + 0.691 < radius:
                                if not self.client.AllowedToBuild(x+i, y+j, z+k) and not overriderank:
                                    self.client.sendServerMessage("You do not have permision to build here.")
                                    return
                                try:
                                    if (i+j+k)%2 == 0:
                                        ticker = 1
                                    else:
                                        ticker = 0
                                    if ticker == 0:
                                        world[x+i, y+j, z+k] = block
                                    else:
                                        world[x+i, y+j, z+k] = block2
                                except AssertionError:
                                    self.client.sendServerMessage("Out of bounds sphere error.")
                                    return
                                if ticker == 0:
                                    self.client.queueTask(TASK_BLOCKSET, (x+i, y+j, z+k, block2), world=world)
                                    self.client.sendBlock(x+i, y+j, z+k, block2)
                                else:
                                    self.client.queueTask(TASK_BLOCKSET, (x+i, y+j, z+k, block), world=world)
                                    self.client.sendBlock(x+i, y+j, z+k, block)
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
                    if fromloc == "user":
                        self.client.sendServerMessage("Your csphere just completed.")
                    pass
            do_step()
            
    @build_list
    @op_only
    def commandCircle(self, parts, fromloc, overriderank):
        "/circle blocktype radius axis [x y z] - Op\nPlace/delete a block and /circle block radius axis"
        if len(parts) < 7 and len(parts) != 4:
            self.client.sendServerMessage("Please enter a type, radius, axis(and possibly a coord triple)")
        else:
            # Try getting the normal axis
            normalAxis = parts[3]
            if normalAxis == 'x' or normalAxis == 'y' or normalAxis == 'z':
                pass
            else:
                self.client.sendServerMessage("Normal axis must be x,y, or z.")
                return
            # Try getting the radius
            try:
                radius = int(parts[2])
            except ValueError:
                self.client.sendServerMessage("Radius must be a Number.")
                return
            # Try getting the block as a direct integer type.
            try:
                block = chr(int(parts[1]))
            except ValueError:
                # OK, try a symbolic type.
                try:
                    block = chr(globals()['BLOCK_%s' % parts[1].upper()])
                except KeyError:
                    self.client.sendServerMessage("'%s' is not a valid block type." % parts[1])
                    return
            # Check the block is valid
            if ord(block) > 49:
                self.client.sendServerMessage("'%s' is not a valid block type." % parts[1])
                return
            # If they only provided the type argument, use the last two block places
            if len(parts) == 4:
                try:
                    x, y, z = self.client.last_block_changes[0]
                except IndexError:
                    self.client.sendServerMessage("You have not clicked for a center yet.")
                    return
            else:
                try:
                    x = int(parts[4])
                    y = int(parts[5])
                    z = int(parts[6])
                except ValueError:
                    self.client.sendServerMessage("All coordinate parameters must be integers.")
                    return
            limit = self.getBuildLimit(overriderank)
            if 2*3.14*(radius)**2>limit:
                self.client.sendServerMessage("Sorry, that area is too big for you to circle.")
                return
            # Draw all the blocks on, I guess
            # We use a generator so we can slowly release the blocks
            # We also keep world as a local so they can't change worlds and affect the new one
            world = self.client.world
            def generate_changes():
                for i in range(-radius-1, radius):
                    for j in range(-radius-1, radius):
                        for k in range(-radius-1, radius):
                            if (i**2 + j**2 + k**2)**0.5 + 0.604 < radius:
                                # Test for axis
                                var_placeblock = 1
                                if i != 0 and normalAxis == 'x':
                                    var_placeblock = 0
                                if j != 0 and normalAxis == 'y':
                                    var_placeblock = 0
                                if k != 0 and normalAxis == 'z':
                                    var_placeblock = 0
                                if var_placeblock == 1:
                                    if not self.client.AllowedToBuild(x+i, y+j, z+k) and not overriderank:
                                        self.client.sendServerMessage("You do not have permission to build here.")
                                        return
                                    try:
                                        world[x+i, y+j, z+k] = block
                                    except AssertionError:
                                        self.client.sendServerMessage("Out of bounds circle error.")
                                        return
                                    self.client.queueTask(TASK_BLOCKSET, (x+i, y+j, z+k, block), world=world)
                                    self.client.sendBlock(x+i, y+j, z+k, block)
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
                    if fromloc == "user":
                        self.client.sendServerMessage("Your circle just completed.")
                    pass
            do_step()

    @build_list
    @op_only
    def commandHCircle(self, parts, fromloc, overriderank):
        "/hcircle blocktype radius axis [x y z] - Op\nPlace/delete a block and /hcircle block radius axis"
        if len(parts) < 7 and len(parts) != 4:
            self.client.sendServerMessage("Please enter a type, radius, axis(and possibly a coord triple)")
        else:
            # Try getting the normal axis
            normalAxis = parts[3]
            if normalAxis == 'x' or normalAxis == 'y' or normalAxis == 'z':
                pass
            else:
                self.client.sendErrorMessage("Normal axis must be x,y, or z.")
                return
            # Try getting the radius
            try:
                radius = int(parts[2])
            except ValueError:
                self.client.sendErrorMessage("Radius must be a Number.")
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
            # If they only provided the type argument, use the last two block places
            if len(parts) == 4:
                try:
                    x, y, z = self.client.last_block_changes[0]
                except IndexError:
                    self.client.sendErrorMessage("You have not clicked for a center yet.")
                    return
            else:
                try:
                    x = int(parts[4])
                    y = int(parts[5])
                    z = int(parts[6])
                except ValueError:
                    self.client.sendServerMessage("All parameters must be integers")
                    return
            limit = self.getBuildLimit(overriderank)
            if 2*3.14*(radius)**2>limit:
                self.client.sendErrorMessage("Sorry, that area is too big for you to hcircle.")
                return
            # Draw all the blocks on, I guess
            # We use a generator so we can slowly release the blocks
            # We also keep world as a local so they can't change worlds and affect the new one
            world = self.client.world
            def generate_changes():
                for i in range(-radius-1, radius):
                    for j in range(-radius-1, radius):
                        for k in range(-radius-1, radius):
                            if (i**2 + j**2 + k**2)**0.5 + .604 < radius and (i**2 + j**2 + k**2)**0.5 + .604 > radius-1.208:
                                # Test for axis
                                var_placeblock = 1
                                if i != 0 and normalAxis == 'x':
                                    var_placeblock = 0
                                if j != 0 and normalAxis == 'y':
                                    var_placeblock = 0
                                if k != 0 and normalAxis == 'z':
                                    var_placeblock = 0
                                if var_placeblock == 1:
                                    if not self.client.AllowedToBuild(x+i, y+j, z+k) and not overriderank:
                                        self.client.sendErrorMessage("You do not have permission to build here.")
                                        return
                                    try:
                                        world[x+i, y+j, z+k] = block
                                    except AssertionError:
                                        self.client.sendErrorMessage("Out of bounds hcircle error.")
                                        return
                                    self.client.queueTask(TASK_BLOCKSET, (x+i, y+j, z+k, block), world=world)
                                    self.client.sendBlock(x+i, y+j, z+k, block)
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
                    if fromloc == "user":
                        self.client.sendServerMessage("Your hcircle just completed.")
                    pass
            do_step()

    @build_list
    @op_only
    def commandHCylinder(self, parts, fromloc, overriderank):
        "/hcyl blocktype radius height axis [x y z] - Op\nPlace/delete a block and /hcyl block radius height axis"
        if len(parts) < 8 and len(parts) != 5:
            self.client.sendServerMessage("Please enter a type, radius, height, axis(and possibly a coord triple)")
        else:
            # Try getting the normal axis
            normalAxis = parts[4]
            if normalAxis == 'x' or normalAxis == 'y' or normalAxis == 'z':
                pass
            else:
                self.client.sendErrorMessage("Normal axis must be x, y, or z.")
                return
            # Try getting the radius
            try:
                radius = int(parts[2])
            except ValueError:
                self.client.sendErrorMessage("Radius must be a Number.")
                return
            # Try getting the height
            try:
                height = parts[3]
            except ValueError:
                self.client.sendErrorMessage("Height must be a Number.")
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
            # If they only provided the type argument, use the last two block places
            if len(parts) == 5:
                try:
                    x, y, z = self.client.last_block_changes[0]
                except IndexError:
                    self.client.sendErrorMessage("You have not clicked for a center yet.")
                    return
            else:
                try:
                    x = int(parts[5])
                    y = int(parts[6])
                    z = int(parts[7])
                except ValueError:
                    self.client.sendServerMessage("All parameters must be integers")
                    return
            limit = self.getBuildLimit(overriderank)
            if 2*3.14*(radius)**2>limit:
                self.client.sendErrorMessage("Sorry, that area is too big for you to hcyl.")
                return
            # Draw all the blocks on, I guess
            # We use a generator so we can slowly release the blocks
            # We also keep world as a local so they can't change worlds and affect the new one
            world = self.client.world
            a, b, c = self.client.last_block_changes[0]
            normalAxis = parts[4]
            if normalAxis == "x":
                def generate_changes():
                    a, b, c = self.client.last_block_changes[0]
                    x, y, z = self.client.last_block_changes[0]
                    height = int(parts[3])
                    while x < (height + a):
                        for i in range(-radius-1, radius):
                            for j in range(-radius-1, radius):
                                for k in range(-radius-1, radius):
                                    if (i**2 + j**2 + k**2)**0.5 + .604 < radius and (i**2 + j**2 + k**2)**0.5 + .604 > radius-1.208:
                                        # Test for axis
                                        var_placeblock = 1
                                        if i != 0 and normalAxis == 'x':
                                            var_placeblock = 0
                                        if j != 0 and normalAxis == 'y':
                                            var_placeblock = 0
                                        if k != 0 and normalAxis == 'z':
                                            var_placeblock = 0
                                        if var_placeblock == 1:
                                            if not self.client.AllowedToBuild(x+i, y+j, z+k) and not overriderank:
                                                self.client.sendErrorMessage("You do not have permission to build here.")
                                                return
                                            try:
                                                world[x+i, y+j, z+k] = block
                                            except AssertionError:
                                                self.client.sendErrorMessage("Out of bounds hcyl error.")
                                                return
                                            self.client.queueTask(TASK_BLOCKSET, (x+i, y+j, z+k, block), world=world)
                                            self.client.sendBlock(x+i, y+j, z+k, block)
                                            yield
                        x += 1
                block_iter = iter(generate_changes())
                def do_step():
                    # Do 10 blocks
                    try:
                        for x in range(10):
                            block_iter.next()
                        reactor.callLater(0.01, do_step)
                    except StopIteration:
                        if fromloc == "user":
                            self.client.sendServerMessage("Your hcyl just completed.")
                        pass
                do_step()
            elif normalAxis == "y":
                def generate_changes():
                    a, b, c = self.client.last_block_changes[0]
                    x, y, z = self.client.last_block_changes[0]
                    height = int(parts[3])
                    while (y < (height + b)):
                        for i in range(-radius-1, radius):
                            for j in range(-radius-1, radius):
                                for k in range(-radius-1, radius):
                                    if (i**2 + j**2 + k**2)**0.5 + .604 < radius and (i**2 + j**2 + k**2)**0.5 + .604 > radius-1.208:
                                        # Test for axis
                                        var_placeblock = 1
                                        if i != 0 and normalAxis == 'x':
                                            var_placeblock = 0
                                        if j != 0 and normalAxis == 'y':
                                            var_placeblock = 0
                                        if k != 0 and normalAxis == 'z':
                                            var_placeblock = 0
                                        if var_placeblock == 1:
                                            if not self.client.AllowedToBuild(x+i, y+j, z+k) and not overriderank:
                                                self.client.sendErrorMessage("You do not have permission to build here.")
                                                return
                                            try:
                                                world[x+i, y+j, z+k] = block
                                            except AssertionError:
                                                self.client.sendErrorMessage("Out of bounds hcyl error.")
                                                return
                                            self.client.queueTask(TASK_BLOCKSET, (x+i, y+j, z+k, block), world=world)
                                            self.client.sendBlock(x+i, y+j, z+k, block)
                                            yield
                        y += 1
                block_iter = iter(generate_changes())
                def do_step():
                    # Do 10 blocks
                    try:
                        for x in range(10):
                            block_iter.next()
                        reactor.callLater(0.01, do_step)
                    except StopIteration:
                        if fromloc == "user":
                            self.client.sendServerMessage("Your hcyl just completed.")
                        pass
                do_step()
            elif normalAxis == "z":
                def generate_changes():
                    a, b, c = self.client.last_block_changes[0]
                    x, y, z = self.client.last_block_changes[0]
                    height = int(parts[3])
                    while z < (height + c):
                        for i in range(-radius-1, radius):
                            for j in range(-radius-1, radius):
                                for k in range(-radius-1, radius):
                                    if (i**2 + j**2 + k**2)**0.5 + .604 < radius and (i**2 + j**2 + k**2)**0.5 + .604 > radius-1.208:
                                        # Test for axis
                                        var_placeblock = 1
                                        if i != 0 and normalAxis == 'x':
                                            var_placeblock = 0
                                        if j != 0 and normalAxis == 'y':
                                            var_placeblock = 0
                                        if k != 0 and normalAxis == 'z':
                                            var_placeblock = 0
                                        if var_placeblock == 1:
                                            if not self.client.AllowedToBuild(x+i, y+j, z+k) and not overriderank:
                                                self.client.sendErrorMessage("You do not have permission to build here.")
                                                return
                                            try:
                                                world[x+i, y+j, z+k] = block
                                            except AssertionError:
                                                self.client.sendErrorMessage("Out of bounds hcyl error.")
                                                return
                                            self.client.queueTask(TASK_BLOCKSET, (x+i, y+j, z+k, block), world=world)
                                            self.client.sendBlock(x+i, y+j, z+k, block)
                                            yield
                        z += 1
                block_iter = iter(generate_changes())
                def do_step():
                    # Do 10 blocks
                    try:
                        for x in range(10):
                            block_iter.next()
                        reactor.callLater(0.01, do_step)
                    except StopIteration:
                        if fromloc == "user":
                            self.client.sendServerMessage("Your hcyl just completed.")
                        pass
                do_step()
            else:
                self.client.sendErrorMessage("The axis must be x, y, or z!")

    @build_list
    @op_only
    def commandCylinder(self, parts, fromloc, overriderank):
        "/cyl blocktype radius height axis [x y z] - Op\nPlace/delete a block and /cyl block radius height axis"
        if len(parts) < 8 and len(parts) != 5:
            self.client.sendServerMessage("Please enter a type, radius, height, axis(and possibly a coord triple)")
        else:
            # Try getting the normal axis
            normalAxis = parts[4]
            if normalAxis == 'x' or normalAxis == 'y' or normalAxis == 'z':
                pass
            else:
                self.client.sendErrorMessage("Normal axis must be x, y, or z.")
                return
            # Try getting the radius
            try:
                radius = int(parts[2])
            except ValueError:
                self.client.sendErrorMessage("Radius must be a Number.")
                return
            # Try getting the height
            try:
                height = parts[3]
            except ValueError:
                self.client.sendErrorMessage("Height must be a Number.")
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
            # If they only provided the type argument, use the last two block places
            if len(parts) == 5:
                try:
                    x, y, z = self.client.last_block_changes[0]
                except IndexError:
                    self.client.sendErrorMessage("You have not clicked for a center yet.")
                    return
            else:
                try:
                    x = int(parts[5])
                    y = int(parts[6])
                    z = int(parts[7])
                except ValueError:
                    self.client.sendServerMessage("All parameters must be integers")
                    return
            limit = self.getBuildLimit(overriderank)
            if 2*3.14*(radius)**2>limit:
                self.client.sendErrorMessage("Sorry, that area is too big for you to make a cylinder.")
                return
            # Draw all the blocks on, I guess
            # We use a generator so we can slowly release the blocks
            # We also keep world as a local so they can't change worlds and affect the new one
            world = self.client.world
            a, b, c = self.client.last_block_changes[0]
            normalAxis = parts[4]
            if normalAxis == "x":
                def generate_changes():
                    a, b, c = self.client.last_block_changes[0]
                    x, y, z = self.client.last_block_changes[0]
                    height = int(parts[3])
                    while x < (height + a):
                        for i in range(-radius-1, radius):
                            for j in range(-radius-1, radius):
                                for k in range(-radius-1, radius):
                                    if (i**2 + j**2 + k**2)**0.5 + .604 < radius:
                                        # Test for axis
                                        var_placeblock = 1
                                        if i != 0 and normalAxis == 'x':
                                            var_placeblock = 0
                                        if j != 0 and normalAxis == 'y':
                                            var_placeblock = 0
                                        if k != 0 and normalAxis == 'z':
                                            var_placeblock = 0
                                        if var_placeblock == 1:
                                            if not self.client.AllowedToBuild(x+i, y+j, z+k) and not overriderank:
                                                self.client.sendErrorMessage("You do not have permission to build here.")
                                                return
                                            try:
                                                world[x+i, y+j, z+k] = block
                                            except AssertionError:
                                                self.client.sendErrorMessage("Out of bounds hcyl error.")
                                                return
                                            self.client.queueTask(TASK_BLOCKSET, (x+i, y+j, z+k, block), world=world)
                                            self.client.sendBlock(x+i, y+j, z+k, block)
                                            yield
                        x += 1
                block_iter = iter(generate_changes())
                def do_step():
                    # Do 10 blocks
                    try:
                        for x in range(10):
                            block_iter.next()
                        reactor.callLater(0.01, do_step)
                    except StopIteration:
                        if fromloc == "user":
                            self.client.sendServerMessage("Your cylinder just completed.")
                        pass
                do_step()
            elif normalAxis == "y":
                def generate_changes():
                    a, b, c = self.client.last_block_changes[0]
                    x, y, z = self.client.last_block_changes[0]
                    height = int(parts[3])
                    while (y < (height + b)):
                        for i in range(-radius-1, radius):
                            for j in range(-radius-1, radius):
                                for k in range(-radius-1, radius):
                                    if (i**2 + j**2 + k**2)**0.5 + .604 < radius:
                                        # Test for axis
                                        var_placeblock = 1
                                        if i != 0 and normalAxis == 'x':
                                            var_placeblock = 0
                                        if j != 0 and normalAxis == 'y':
                                            var_placeblock = 0
                                        if k != 0 and normalAxis == 'z':
                                            var_placeblock = 0
                                        if var_placeblock == 1:
                                            if not self.client.AllowedToBuild(x+i, y+j, z+k) and not overriderank:
                                                self.client.sendErrorMessage("You do not have permission to build here.")
                                                return
                                            try:
                                                world[x+i, y+j, z+k] = block
                                            except AssertionError:
                                                self.client.sendErrorMessage("Out of bounds hcyl error.")
                                                return
                                            self.client.queueTask(TASK_BLOCKSET, (x+i, y+j, z+k, block), world=world)
                                            self.client.sendBlock(x+i, y+j, z+k, block)
                                            yield
                        y += 1
                block_iter = iter(generate_changes())
                def do_step():
                    # Do 10 blocks
                    try:
                        for x in range(10):
                            block_iter.next()
                        reactor.callLater(0.01, do_step)
                    except StopIteration:
                        if fromloc == "user":
                            self.client.sendServerMessage("Your cylinder just completed.")
                        pass
                do_step()
            elif normalAxis == "z":
                def generate_changes():
                    a, b, c = self.client.last_block_changes[0]
                    x, y, z = self.client.last_block_changes[0]
                    height = int(parts[3])
                    while z < (height + c):
                        for i in range(-radius-1, radius):
                            for j in range(-radius-1, radius):
                                for k in range(-radius-1, radius):
                                    if (i**2 + j**2 + k**2)**0.5 + .604 < radius:
                                        # Test for axis
                                        var_placeblock = 1
                                        if i != 0 and normalAxis == 'x':
                                            var_placeblock = 0
                                        if j != 0 and normalAxis == 'y':
                                            var_placeblock = 0
                                        if k != 0 and normalAxis == 'z':
                                            var_placeblock = 0
                                        if var_placeblock == 1:
                                            if not self.client.AllowedToBuild(x+i, y+j, z+k) and not overriderank:
                                                self.client.sendErrorMessage("You do not have permission to build here.")
                                                return
                                            try:
                                                world[x+i, y+j, z+k] = block
                                            except AssertionError:
                                                self.client.sendErrorMessage("Out of bounds hcyl error.")
                                                return
                                            self.client.queueTask(TASK_BLOCKSET, (x+i, y+j, z+k, block), world=world)
                                            self.client.sendBlock(x+i, y+j, z+k, block)
                                            yield
                        z += 1
                block_iter = iter(generate_changes())
                def do_step():
                    # Do 10 blocks
                    try:
                        for x in range(10):
                            block_iter.next()
                        reactor.callLater(0.01, do_step)
                    except StopIteration:
                        if fromloc == "user":
                            self.client.sendServerMessage("Your cylinder just completed.")
                        pass
                do_step()
            else:
                self.client.sendErrorMessage("The axis must be x, y, or z!")

    @build_list
    @op_only
    def commandDome(self, parts, fromloc, overriderank):
        "/dome blocktype radius fill [x y z] - Op\nPlace/delete a block and /sphere block radius"
        if len(parts) < 7 and len(parts) != 4:
            self.client.sendServerMessage("Please enter a type radius and fill?(and possibly a coord triple)")
        else:
            # Try getting the fill
            fill = parts[3]
            if fill=='true' or fill=='false':
                pass
            else:
                self.client.sendServerMessage("fill must be true or false")
                return
            # Try getting the radius
            try:
                radius = int(parts[2])
            except ValueError:
                self.client.sendServerMessage("Radius must be a Number.")
                return
            # Try getting the block as a direct integer type.
            try:
                block = chr(int(parts[1]))
            except ValueError:
                # OK, try a symbolic type.
                try:
                    block = chr(globals()['BLOCK_%s' % parts[1].upper()])
                except KeyError:
                    self.client.sendServerMessage("'%s' is not a valid block type." % parts[1])
                    return
            # Check the block is valid
            if ord(block) > 49:
                self.client.sendServerMessage("'%s' is not a valid block type." % parts[1])
                return
            # If they only provided the type argument, use the last two block places
            if len(parts) == 4:
                try:
                    x, y, z = self.client.last_block_changes[0]
                except IndexError:
                    self.client.sendServerMessage("You have not clicked for a center yet.")
                    return
            else:
                try:
                    x = int(parts[4])
                    y = int(parts[5])
                    z = int(parts[6])
                except ValueError:
                    self.client.sendServerMessage("All coordinate parameters must be integers.")
                    return
            absradius = abs(radius)
            limit = self.getBuildLimit(overriderank)
            if (radius*2)**3/2>limit:
                self.client.sendServerMessage("Sorry, that area is too big for you to dome.")
                return
            # Draw all the blocks on, I guess
            # We use a generator so we can slowly release the blocks
            # We also keep world as a local so they can't change worlds and affect the new one
            world = self.client.world
            def generate_changes():
                for i in range(-absradius-1, absradius):
                    for j in range(-absradius-1, absradius):
                        for k in range(-absradius-1, absradius):
                            if ((i**2 + j**2 + k**2)**0.5 + 0.691 < absradius and ((j >= 0 and radius > 0) or (j <= 0 and radius < 0)) and fill=='true') or (absradius-1 < (i**2 + j**2 + k**2)**0.5 + 0.691 < absradius and ((j >= 0 and radius > 0) or (j <= 0 and radius < 0)) and fill=='false'):
                                if not self.client.AllowedToBuild(x+i, y+j, z+k) and not overriderank:
                                    self.client.sendServerMessage("You do not have permision to build here.")
                                    return
                                try:
                                    world[x+i, y+j, z+k] = block
                                except AssertionError:
                                    self.client.sendServerMessage("Out of bounds dome error.")
                                    return
                                self.client.queueTask(TASK_BLOCKSET, (x+i, y+j, z+k, block), world=world)
                                self.client.sendBlock(x+i, y+j, z+k, block)
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
                    if fromloc == "user":
                        self.client.sendServerMessage("Your dome just completed.")
                    pass
            do_step()

    @build_list
    @op_only
    def commandEllipsoid(self, parts, fromloc, overriderank):
        "/ellipsoid blocktype endradius [x y z x2 y2 z2] - Op\nAliases: ell\nPlace/delete two blocks and block endradius"
        if len(parts) < 9 and len(parts) != 3:
            self.client.sendServerMessage("Please enter a type endradius (and possibly two coord triples)")
        else:
            # Try getting the radius
            try:
                endradius = int(parts[2])
            except ValueError:
                self.client.sendServerMessage("Endradius must be a Number.")
                return
            # Try getting the block as a direct integer type.
            try:
                block = chr(int(parts[1]))
            except ValueError:
                # OK, try a symbolic type.
                try:
                    block = chr(globals()['BLOCK_%s' % parts[1].upper()])
                except KeyError:
                    self.client.sendServerMessage("'%s' is not a valid block type." % parts[1])
                    return
            # Check the block is valid
            if ord(block) > 49:
                self.client.sendServerMessage("'%s' is not a valid block type." % parts[1])
                return
            # If they only provided the type argument, use the last two block places
            if len(parts) == 3:
                try:
                    x, y, z = self.client.last_block_changes[0]
                    x2, y2, z2 = self.client.last_block_changes[1]
                except IndexError:
                    self.client.sendServerMessage("You have not clicked two points yet.")
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
            limit = self.getBuildLimit(overriderank)
            radius = int(round(endradius*2 + ((x2-x)**2+(y2-y)**2+(z2-z)**2)**0.5)/2 + 1)
            var_x = int(round(float(x+x2)/2))
            var_y = int(round(float(y+y2)/2))
            var_z = int(round(float(z+z2)/2))
            if int(4/3*3.14*radius**2*endradius)>limit:
                self.client.sendServerMessage("Sorry, that area is too big for you to ellipsoid.")
                return
            # Draw all the blocks on, I guess
            # We use a generator so we can slowly release the blocks
            # We also keep world as a local so they can't change worlds and affect the new one
            world = self.client.world
            def generate_changes():
                for i in range(-radius-2, radius+1):
                    for j in range(-radius-2, radius+1):
                        for k in range(-radius-2, radius+1):
                            if (((i+var_x-x)**2 + (j+var_y-y)**2 + (k+var_z-z)**2)**0.5 + ((i+var_x-x2)**2 + (j+var_y-y2)**2 + (k+var_z-z2)**2)**0.5)/2 + 0.691 < radius:
                                if not self.client.AllowedToBuild(x+i, y+j, z+k) and not overriderank:
                                    self.client.sendServerMessage("You do not have permision to build here.")
                                    return
                                try:
                                    world[var_x+i, var_y+j, var_z+k] = block
                                except AssertionError:
                                    self.client.sendServerMessage("Out of bounds ellipsoid error.")
                                    return
                                self.client.queueTask(TASK_BLOCKSET, (var_x+i, var_y+j, var_z+k, block), world=world)
                                self.client.sendBlock(var_x+i, var_y+j, var_z+k, block)
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
                    if fromloc == "user":
                        self.client.sendServerMessage("Your ellipsoid just completed.")
                    pass
            do_step()

    @build_list
    @op_only
    def commandPolytri(self, parts, fromloc, overriderank):
        "/polytri blockname [x y z x2 y2 z2 x3 y3 z3] - Op\nSets all blocks between three points to block."
        if len(parts) < 11 and len(parts) != 2:
            self.client.sendServerMessage("Please enter a type (and possibly three coord triples)")
        else:
            # Try getting the block as a direct integer type.
            try:
                block = chr(int(parts[1]))
            except ValueError:
                # OK, try a symbolic type.
                try:
                    block = chr(globals()['BLOCK_%s' % parts[1].upper()])
                except KeyError:
                    self.client.sendServerMessage("'%s' is not a valid block type." % parts[1])
                    return
            # Check the block is valid
            if ord(block) > 49:
                self.client.sendServerMessage("'%s' is not a valid block type." % parts[1])
                return
            op_blocks = [BLOCK_SOLID, BLOCK_WATER, BLOCK_LAVA]
            if ord(block) in op_blocks and not self.client.isOpPlus():
                self.client.sendServerMessage("Sorry, but you can't use that block.")
                return
            # If they only provided the type argument, use the last two block places
            if len(parts) == 2:
                try:
                    x, y, z = self.client.last_block_changes[0]
                    x2, y2, z2 = self.client.last_block_changes[1]
                    x3, y3, z3 = self.client.last_block_changes[2]
                except:
                    self.client.sendServerMessage("You have not clicked 3 points yet.")
                    return
            else:
                try:
                    x = int(parts[2])
                    y = int(parts[3])
                    z = int(parts[4])
                    x2 = int(parts[5])
                    y2 = int(parts[6])
                    z2 = int(parts[7])
                    x3 = int(parts[8])
                    y3 = int(parts[9])
                    z3 = int(parts[10])
                except ValueError:
                    self.client.sendServerMessage("All coordinate parameters must be integers.")
                    return
            # line 1 list
            steps = int(((x2-x)**2+(y2-y)**2+(z2-z)**2)**0.5/0.75)
            mx = float(x2-x)/steps
            my = float(y2-y)/steps
            mz = float(z2-z)/steps
            coordinatelist2 = []
            for t in range(steps+1):
                coordinatelist2.append((mx*t+x,my*t+y,mz*t+z))
            # line 2 list
            steps = int(((x3-x)**2+(y3-y)**2+(z3-z)**2)**0.5/0.75)
            mx = float(x3-x)/steps
            my = float(y3-y)/steps
            mz = float(z3-z)/steps
            coordinatelist3 = []
            for t in range(steps+1):
                coordinatelist3.append((mx*t+x,my*t+y,mz*t+z))
            # final coordinate list
            if len(coordinatelist2) > len(coordinatelist3):
                coordinatelistA = coordinatelist2
                coordinatelistB = coordinatelist3
            else:
                coordinatelistA = coordinatelist3
                coordinatelistB = coordinatelist2
            lenofA = len(coordinatelistA)
            listlenRatio = float(len(coordinatelistB))/lenofA
            finalcoordinatelist = []
            for i in range(lenofA):
                point1 = coordinatelistA[i]
                point2 = coordinatelistB[int(i*listlenRatio)]
                var_x = point1[0]
                var_y = point1[1]
                var_z = point1[2]
                var_x2 = point2[0]
                var_y2 = point2[1]
                var_z2 = point2[2]
                steps = int(((var_x2-var_x)**2+(var_y2-var_y)**2+(var_z2-var_z)**2)**0.5/0.75)
                if steps != 0:
                    mx = float(var_x2-var_x)/steps
                    my = float(var_y2-var_y)/steps
                    mz = float(var_z2-var_z)/steps
                    coordinatelist = []
                    for t in range(steps+1):
                        coordinatelist.append((int(round(mx*t+var_x)),int(round(my*t+var_y)),int(round(mz*t+var_z))))
                    for coordtuple in coordinatelist:
                        if coordtuple not in finalcoordinatelist:
                            finalcoordinatelist.append(coordtuple)
                elif point1 not in finalcoordinatelist:
                    finalcoordinatelist.append(point1)
            limit = self.getBuildLimit(overriderank)
            # Stop them doing silly things
            if ((x-x2)**2+(y-y2)**2+(z-z2)**2)**0.5*((x-x3)**2+(y-y3)**2+(z-z3)**2)**0.5 > limit:
                self.client.sendServerMessage("Sorry, that area is too big for you to polytri.")
                return
            # Draw all the blocks on, I guess
            # We use a generator so we can slowly release the blocks
            # We also keep world as a local so they can't change worlds and affect the new one
            world = self.client.world
            def generate_changes():
                for coordtuple in finalcoordinatelist:
                    i = int(coordtuple[0])
                    j = int(coordtuple[1])
                    k = int(coordtuple[2])
                    if not self.client.AllowedToBuild(i, j, k) and not overriderank:
                        self.client.sendServerMessage("You do not have permision to build here.")
                        return
                    try:
                        world[i, j, k] = block
                    except AssertionError:
                        self.client.sendServerMessage("Out of bounds polytri error.")
                        return
                    self.client.queueTask(TASK_BLOCKSET, (i, j, k, block), world=world)
                    self.client.sendBlock(i, j, k, block)
                    yield
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
                        self.client.sendServerMessage("Your polytri just completed.")
                    pass
            do_step()

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
