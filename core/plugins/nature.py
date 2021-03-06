# The Nexus software is licensed under the BSD 2-Clause license.
#
# You should have recieved a copy of this license with the software.
# If you did not, you can find one at the following link.
#
# http://opensource.org/licenses/bsd-license.php


import math, random
from reqs.twisted.internet import reactor
from core.plugins import ProtocolPlugin
from core.decorators import *
from core.constants import *

class ToolsPlugin(ProtocolPlugin):
    
    commands = {
        "dune": "commandDune",
        "hill": "commandHill",
        "hole": "commandHole",
        "lake": "commandLake",
        "mountain": "commandMountain",
        "pit": "commandPit",
        "tree": "commandTree",
    }

    hooks = {
        "blockchange": "blockChanged",
        "newworld": "newWorld",
    }
    
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
