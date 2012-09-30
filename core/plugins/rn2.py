import threading
from reqs.twisted.internet import reactor
from core.plugins import ProtocolPlugin
from core.decorators import *
from core.protocol import *
from core.constants import *

class ReplaceNearPlugin(ProtocolPlugin):

    commands = {
        "rn2": "commandReplaceNearInstant",

        }



    @builder_only
    def commandReplaceNearInstant(self, parts, fromloc, overriderank):
        "/rn2 <radius> <blocktoreplace> <blockreplacing> - Builder\nAliases: /rn"
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
            if len(parts) == 2:
                try:
                    x, y, z = self.client.last_block_changes[0]
                except IndexError:
                    self.client.sendServerMessage("You have not clicked a block yet.")
                    return
            else:
                x, y, z = self.client.last_block_changes[0]
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
            #keep the building in the current world
            world = self.client.world
            """#draw the blocks on
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
            do_step()"""


            if limit >= 45565: # To test it out first, will try a bigger one later - tyteen
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
                        for i in range(x-size, x+size):
                            for j in range(y-size, y+size):
                                for k in range(z-size, z+size):
                                    if not self.client.AllowedToBuild(i, j, k) and not overriderank:
                                        return
                                    world[i, j, k] = blockB
                        self.client.sendServerMessage("Replacenear finished. Respawning...")
                        return True
                    except AssertionError:
                        self.client.sendErrorMessage("Out of bounds replacenear error.")
                        return
                threading.Thread(target=doBlocks).start()
                # Now the fun part. Respawn them all!
                for client in world.clients:
                    self.client.queueTask(TASK_INSTANTRESPAWN, self.client.username, world=world)
                if fromloc == "user":
                    self.client.sendServerMessage("Your replacenear just completed.")
            else:
                def generate_changes():
                    try:
                        for i in range(x-size, x+size):
                            for j in range(y-size, y+size):
                                for k in range(z-size, z+size):
                                    if not self.client.AllowedToBuild(i, j, k) and not overriderank:
                                        return
                                    world[i, j, k] = blockB
                                    self.client.runHook("blockchange", x, y, z, ord(block), ord(block), fromloc)
                                    self.client.queueTask(TASK_BLOCKSET, (i, j, k, blockB), world=world)
                                    self.client.sendBlock(i, j, k, blockB)
                                    yield
                    except AssertionError:
                        self.client.sendErrorMessage("Out of bounds replacenear error.")
                        return
                block_iter = iter(generate_changes())
                def do_step():
                    try:
                        for x in range(10):
                            block_iter.next()
                        reactor.callLater(0.01, do_step)
                    except StopIteration:
                        if fromloc == "user":
                            self.client.sendServerMessage("Your replacenear just completed.")
                        pass
                do_step()
