# The Nexus software is licensed under the BSD 2-Clause license.
#
# You should have recieved a copy of this license with the software.
# If you did not, you can find one at the following link.
#
# http://opensource.org/licenses/bsd-license.php


x,y,z = var_position
userpositionlist = []
for user in clients:
    userpositionlist.append((user.x >> 5,user.y >> 5,user.z >> 5))
closestposition = (0,0)
closestclient = None
closestdistance = None
for var_pos in userpositionlist:
    i,j,k = var_pos
    distance = ((i-x)**2+(j-y)**2+(k-z)**2)**0.5
    if closestdistance == None:
        closestdistance = distance
        closestposition = (var_pos[0],var_pos[2])
    else:
        if distance < closestdistance:
            closestdistance = distance
            closestposition = (var_pos[0],var_pos[2])
i,k = closestposition
distance = ((i-x)**2+(k-z)**2)**0.5
if distance != 0 and distance > 2:
    target = [int((i-x)/(distance/1.75)) + x,int((j-y)/(distance/1.75)) + y,int((k-z)/(distance/1.75)) + z]
    i,j,k = target
    var_cango = True
    try:
        blocktocheck = ord(world.blockstore.raw_blocks[world.blockstore.get_offset(i,j,k)])
        if blocktocheck != 0:
            var_cango = False
    except:
        var_cango = False
    if var_cango:
        block = chr(0)
        try:
            world[x, y, z] = block
        except:
            world[x, y, z] = block
        self.client.queueTask(TASK_BLOCKSET, (x, y, z, block), world=world)
        self.client.sendBlock(x, y, z, block)
        var_position = target
        x,y,z = var_position
        block = chr(35)
        try:
            world[x, y, z] = block
        except:
            world[x, y, z] = block
        self.client.queueTask(TASK_BLOCKSET, (x, y, z, block), world=world)
        self.client.sendBlock(x, y, z, block)
    else:
        var_cango = True
        target[1] = target[1] + 1
        j = target[1]
        try:
            blocktocheck = ord(world.blockstore.raw_blocks[world.blockstore.get_offset(i,j,k)])
            if blocktocheck != 0:
                var_cango = False
        except:
            var_cango = False
        if var_cango:
            block = chr(0)
            try:
                world[x, y, z] = block
            except:
                world[x, y, z] = block
            self.client.queueTask(TASK_BLOCKSET, (x, y, z, block), world=world)
            self.client.sendBlock(x, y, z, block)
            var_position = target
            x,y,z = var_position
            block = chr(35)
            try:
                world[x, y, z] = block
            except:
                world[x, y, z] = block
            self.client.queueTask(TASK_BLOCKSET, (x, y, z, block), world=world)
            self.client.sendBlock(x, y, z, block)
