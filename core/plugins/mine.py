# The Nexus software is licensed under the BSD 2-Clause license.
#
# You should have recieved a copy of this license with the software.
# If you did not, you can find one at the following link.
#
# http://opensource.org/licenses/bsd-license.php


from core.plugins import ProtocolPlugin
from core.decorators import *
from core.constants import *
from reqs.twisted.internet import reactor

class DynamitePlugin(ProtocolPlugin):

    commands = {
        "mine": "commandMine",
        "clearmines": "commandClear",
    }

    hooks = {
        "blockchange": "blockChanged",
        "poschange": "posChanged",
    }

    def blockChanged(self, x, y, z, block, selected_block, fromloc):
        if fromloc != "user":
            # People shouldn't be blbing mines
            return
        if self.client.world.has_mine(x, y, z):
            self.client.sendServerMessage("You defused a mine!")
            self.client.world.delete_mine(x, y, z)
        if self.placingmines and block==BLOCK_BLACK:
            self.client.sendServerMessage("You placed a mine")
            self.placingmines = False
            def ActivateMine():
                self.client.world.add_mine(x, y, z)
                self.client.sendServerMessage("Your mine is now active!")
            reactor.callLater(2, ActivateMine)

    def posChanged(self, x, y, z, h, p):
        "Hook trigger for when the user moves"
        rx = x >> 5
        ry = y >> 5
        rz = z >> 5
        mx = rx
        mz = rz
        my = ry - 2
        try:
            if self.client.world.has_mine(mx, my, mz) or self.client.world.has_mine(mx, my-1, mz):
                if self.client.world.has_mine(mx, my-1, mz):
                    self.client.world.delete_mine(mx, my-1, mz)            
                    my = ry - 3
                if self.client.world.has_mine(mx, my, mz):
                    my = ry - 2
                    self.client.world.delete_mine(mx, my, mz)
                tobuild = []
                # Randomise the variables
                fanout = self.explosion_radius
                def explode():
                    # Clear the explosion radius
                    for i in range(-fanout, fanout+1):
                        for j in range(-fanout, fanout+1):
                            for k in range(-fanout, fanout+1):
                                if (i**2+j**2+k**2)**0.5 + 0.691 < fanout:
                                    if not self.client.AllowedToBuild(mx+i, my+j, mz+k):
                                        return
                                    check_offset = self.client.world.blockstore.get_offset(mx+i, my+j, mz+k)
                                    blocktype = self.client.world.blockstore.raw_blocks[check_offset]
                                    unbreakables = [chr(BLOCK_SOLID), chr(BLOCK_IRON), chr(BLOCK_GOLD)]
                                    if blocktype not in unbreakables:
                                        if not self.client.world.has_mine(mx+i, my+j, mz+k):
                                            tobuild.append((i, j, k, BLOCK_STILLLAVA))
                    # OK, send the build changes
                    for dx, dy, dz, block in tobuild:
                        try:
                            self.client.world[mx+dx, my+dy, mz+dz] = chr(block)
                            self.client.sendBlock(mx+dx, my+dy, mz+dz, block)
                            self.client.factory.queue.put((self.client, TASK_BLOCKSET, (mx+dx, my+dy, mz+dz, block)))
                        except AssertionError: # OOB
                            pass
                def explode2():
                    # Clear the explosion radius
                    for i in range(-fanout, fanout+1):
                        for j in range(-fanout, fanout+1):
                            for k in range(-fanout, fanout+1):
                                if (i**2+j**2+k**2)**0.5 + 0.691 < fanout:
                                    if not self.client.AllowedToBuild(mx+i, my+j, mz+k):
                                        return
                                    check_offset = self.client.world.blockstore.get_offset(mx+i, my+j, mz+k)
                                    blocktype = self.client.world.blockstore.raw_blocks[check_offset]
                                    unbreakables = [chr(BLOCK_SOLID), chr(BLOCK_IRON), chr(BLOCK_GOLD)]
                                    if blocktype not in unbreakables:
                                        if not self.client.world.has_mine(mx+i, my+j, mz+k):
                                            tobuild.append((i, j, k, BLOCK_AIR))
                    # OK, send the build changes
                    for dx, dy, dz, block in tobuild:
                        try:
                            self.client.world[mx+dx, my+dy, mz+dz] = chr(block)
                            self.client.sendBlock(mx+dx, my+dy, mz+dz, block)
                            self.client.factory.queue.put((self.client, TASK_BLOCKSET, (mx+dx, my+dy, mz+dz, block)))
                        except AssertionError: # OOB
                            pass
                # Explode in 2 seconds
                self.client.sendServerMessage("*CLICK*")
                reactor.callLater(self.delay, explode)
                # Explode2 in 3 seconds
                reactor.callLater(self.delay+0.5, explode2)
        except AssertionError:
            # oob
            pass                

    @build_list
    @op_only
    def commandMine(self, parts, fromloc, rankoverride):
        "/mine - Op\nMakes the next black block you place a mine."
        self.placingmines = True
        self.client.sendServerMessage("You are now placing mine blocks.")
        self.client.sendServerMessage("Place a black block.")

    @build_list
    @admin_only
    def commandClear(self, parts, fromloc, rankoverride):
        self.client.world.clear_mines()
        self.client.sendServerMessage("You cleared all mines")

    def gotClient(self):
        self.explosion_radius = 3
        self.delay = .5
        self.placingmines = False
