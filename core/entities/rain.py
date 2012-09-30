# The Nexus software is licensed under the BSD 2-Clause license.
#
# You should have recieved a copy of this license with the software.
# If you did not, you can find one at the following link.
#
# http://opensource.org/licenses/bsd-license.php


x,y,z = var_position
i = x
j = -1 + y
k = z
var_cango = True
block = chr(0)
try:
    world[x, y, z] = block
except:
    world[x, y, z] = block
self.client.queueTask(TASK_BLOCKSET, (x, y, z, block), world=world)
self.client.sendBlock(x, y, z, block)
try:
    blocktocheck = ord(world.blockstore.raw_blocks[world.blockstore.get_offset(i, j, k)])
    if blocktocheck != 0:
        var_cango = False
except:
    var_cango = False
if var_cango and randint(0,45) != 45:
    var_position = (i,j,k)
    x,y,z = var_position
    block = chr(9) 
    try:
        world[x, y, z] = block
    except:
        world[x, y, z] = block
    self.client.queueTask(TASK_BLOCKSET, (x, y, z, block), world=world)
    self.client.sendBlock(x, y, z, block)
else:
    blocktocheck = ord(world.blockstore.raw_blocks[world.blockstore.get_offset(i, j, k)])
    if blocktocheck != 0:
        var_cango = False
        var_dellist.append(index)
