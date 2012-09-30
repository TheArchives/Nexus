# The Nexus software is licensed under the BSD 2-Clause license.
#
# You should have recieved a copy of this license with the software.
# If you did not, you can find one at the following link.
#
# http://opensource.org/licenses/bsd-license.php


if world.blockstore.raw_blocks[world.blockstore.get_offset(x,y+1,z)] != '\x14':
    block = chr(20)
    world[x, y+1, z] = block
    self.client.queueTask(TASK_BLOCKSET, (x, y+1, z, block), world=world)
    self.client.sendBlock(x, y+1, z, block)
for client in worldblockchangesdict:
    cx,cy,cz,var_timeofchange = worldblockchangesdict[client][0][:4]
    if (cx,cy,cz) == (x,y+1,z) and time()- var_timeofchange < 2:
        worldblockchangedellist.append(client)
        px,py,pz,ph,pp = worldblockchangesdict[client][1]
        client.sendServerMessage("Your x,y,z,h,p is: " + str((px,py,pz,ph,pp)))
        h = math.radians(ph*360.0/256.0)
        p = math.radians(pp*360.0/256.0)
        rx,ry,rz = math.sin(h)*math.cos(p),-math.sin(p),-math.cos(h)*math.cos(p)
        client.sendServerMessage("You are facing the ray:")
        client.sendServerMessage(str((rx,ry,rz)))
        client.sendServerMessage("Test: " + str(math.sqrt(math.pow(rx,2) + math.pow(ry,2) + math.pow(rz,2))))
