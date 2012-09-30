# The Nexus software is licensed under the BSD 2-Clause license.
#
# You should have recieved a copy of this license with the software.
# If you did not, you can find one at the following link.
#
# http://opensource.org/licenses/bsd-license.php


if world.blockstore.raw_blocks[world.blockstore.get_offset(x,y+1,z)] != '\x14':
    block = '\x14'
    world[x, y+1, z] = block
    self.client.queueTask(TASK_BLOCKSET, (x, y+1, z, block), world=world)
    self.client.sendBlock(x, y+1, z, block)
if entity[4] not in entities_childerenlist:
    for client in worldblockchangesdict:
        cx,cy,cz,var_timeofchange = worldblockchangesdict[client][0][:4]
        if (cx,cy,cz) == (x,y+1,z) and time()- var_timeofchange < 2:
            worldblockchangedellist.append(client)
            i = world.entities_childerenlist_index
            world.entities_childerenlist_index += 1
            entities_childerenlist.append(i)
            entity[4] = i
            px,py,pz,ph,pp = worldblockchangesdict[client][1]
            distancebetween = ((x-px)**2+(y+1-py)**2+(z-pz)**2)**0.5
            h = math.radians(ph*360.0/256.0)
            p = math.radians(pp*360.0/256.0)
            rx,ry,rz = math.sin(h)*math.cos(p),-math.sin(p),-math.cos(h)*math.cos(p)
            entitylist.append(["testarrow",(rx*distancebetween+rx+px,ry*distancebetween+ry+py,rz*distancebetween+rz+pz),2,2,(rx,ry,rz),i])
