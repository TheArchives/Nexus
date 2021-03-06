# The Nexus software is licensed under the BSD 2-Clause license.
#
# You should have recieved a copy of this license with the software.
# If you did not, you can find one at the following link.
#
# http://opensource.org/licenses/bsd-license.php


from reqs.twisted.internet import reactor
from core.plugins import ProtocolPlugin
from core.decorators import *
from core.constants import *

class StairsPlugin(ProtocolPlugin):
    
    commands = {
        "stairs": "commandStairs",
    }
    
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
