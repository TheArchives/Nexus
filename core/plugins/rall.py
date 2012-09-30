import threading, math, random, sys
from reqs.twisted.internet import reactor
from core.plugins import ProtocolPlugin
from core.decorators import *
from core.constants import *

class RAllPlugin(ProtocolPlugin):
    commands = {
        "rall": "commandReplaceAll",
        "replaceall": "commandReplaceAll",
        "repall": "commandReplaceAll",
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
    @worldowner_only
    def commandReplaceAll(self, parts, fromloc, overriderank):
        "/replaceall blockA blockB - World Owner\nAliases: rall, repall\nReplaces all blocks of blockA in the current world to blockB."
        if len(parts) != 3:
            self.client.sendServerMessage("Please enter types.")
        else:
            blockA = self.client.GetBlockValue(parts[1])
            blockB = self.client.GetBlockValue(parts[2])
            if blockA == None or blockB == None:
                return

            x, y, z = 0, 0, 0
            x2, y2, z2 = self.client.world.x - 1, self.client.world.y - 1, self.client.world.z - 1
            
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
