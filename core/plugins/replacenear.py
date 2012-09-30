import threading
from reqs.twisted.internet import reactor
from core.plugins import ProtocolPlugin
from core.decorators import *
from core.protocol import *
from core.constants import *

class ReplaceNearPlugin(ProtocolPlugin):

    commands = {
        "replacenear": "commandReplaceNear",
        "rn": "commandReplaceNear",

        }



    @builder_only
    def commandReplaceNear(self, parts, byuser, overriderank):
        "/replacenear <radius> <blocktoreplace> <blockreplacing> - Builder\nAliases: /rn"
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
