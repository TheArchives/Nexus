# The Nexus software is licensed under the BSD 2-Clause license.
#
# You should have recieved a copy of this license with the software.
# If you did not, you can find one at the following link.
#
# http://opensource.org/licenses/bsd-license.php


bombintialdelay = entity[5]
bombfinaldelay = entity[6]
if bombintialdelay <= 0:
    if entity[4]:
        entity[4] = False
        var_userkillist = []
        var_userkillist2 = []
        block = '\x0b'
        for entry in userpositionlist:
            tx,ty,tz = entry[1]
            distance = ((tx-x)**2+(ty-y)**2+(tz-z)**2)**0.5
            if distance < 4:
                var_userkillist.append(entry[0])
        for i,j,k in explosionblocklist:
            for var_index in range(len(entitylist)):
                var_entity = entitylist[var_index]
                identity = var_entity[0]
                if identity != "tnt" and identity != "smoke":
                    rx,ry,rz = var_entity[1]
                    dx,dy,dz = (i+x,j+y,k+z)
                    if (rx,ry,rz) == (dx,dy,dz) or (identity in twoblockhighentities and (rx,ry+1,rz) == (dx,dy,dz)):
                        var_dellist.append(var_index)
            ax,ay,az = (i+x,j+y,k+z)
            try:
                if world.blockstore.raw_blocks[world.blockstore.get_offset(ax,ay,az)] not in var_unbreakables:
                    world[ax,ay, az] = block
                    self.client.queueTask(TASK_BLOCKSET, (ax, ay, az, block), world=world)
                    self.client.sendBlock(ax, ay, az, block)
            except:
                pass
        for user in var_userkillist:
            if user not in var_userkillist2:
                var_userkillist2.append(user)
        for user in var_userkillist2:
            sx,sy,sz,sh = world.spawn
            user.teleportTo(sx,sy,sz,sh)
            self.client.sendWorldMessage("%s has died from TNT (or a creeper?)" % user.username)
    if bombfinaldelay <=0:
        var_dellist.append(index)
        block = '\x00'
        for i,j,k in explosionblocklist:
            ax,ay,az = (i+x,j+y,k+z)
            try:
                if world.blockstore.raw_blocks[world.blockstore.get_offset(ax,ay,az)] not in var_unbreakables:
                    world[ax,ay, az] = block

                    self.client.queueTask(TASK_BLOCKSET, (ax, ay, az, block), world=world)
                    self.client.sendBlock(ax, ay, az, block)
            except:
                pass
        world[x,y,z] = block
        self.client.queueTask(TASK_BLOCKSET, (x, y, z, block), world=world)
        self.client.sendBlock(x, y, z, block)
        entitylist.append(["smoke",(x,y,z),4,4,True])
        entitylist.append(["smoke",(x,y+2,z),4,4,True])
        entitylist.append(["smoke",(x,y+1,z+1),4,4,True])
        entitylist.append(["smoke",(x+1,y+1,z),4,4,True])
        entitylist.append(["smoke",(x+1,y-1,z),4,4,True])
        entitylist.append(["smoke",(x,y-1,z-1),4,4,True])
        entitylist.append(["smoke",(x,y-1,z+1),4,4,True])
    else:
        bombfinaldelay -= 1
else:
    bombintialdelay -= 1
entity[5] = bombintialdelay
entity[6] = bombfinaldelay
