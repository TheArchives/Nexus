# The Nexus software is licensed under the BSD 2-Clause license.
#
# You should have recieved a copy of this license with the software.
# If you did not, you can find one at the following link.
#
# http://opensource.org/licenses/bsd-license.php


var_cango = True
if entity[5] >= 3:
    i = randint(-1,1)
    k = randint(-1,1)
    j = randint(-1,1)
    entity[4] = (i,j,k)
    entity[5] = 0
entity[5] = randint(1,5)
l, m, n = entity[4]
try:
    blocktocheck = ord(world.blockstore.raw_blocks[world.blockstore.get_offset(x+l,y+m,z+n)])
    if blocktocheck != 8:
        var_cango = False
except:
    pass
if var_cango:
    block = 8
    self.client.queueTask(TASK_BLOCKSET, (x,y,z, block), world=world)
    self.client.sendBlock(x,y,z, block)
    if entity[6]:
        block = randint(22,36)
    else:
        block = 22
    self.client.queueTask(TASK_BLOCKSET, (x+l,y+m,z+n, block), world=world)
    self.client.sendBlock(x+l,y+m,z+n, block)
    var_position = (x+l,y+m,z+n)
    x,y,z = var_position
