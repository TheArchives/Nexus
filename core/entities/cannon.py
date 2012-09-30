#    iCraft is Copyright 2010-2011 both
#
#    The Archives team:
#                   <Adam Guy> adam@adam-guy.com AKA "Adam01"
#                   <Andrew Godwin> andrew@aeracode.org AKA "Aera"
#                   <Dylan Lukes> lukes.dylan@gmail.com AKA "revenant"
#                   <Gareth Coles> colesgareth2@hotmail.com AKA "gdude2002"
#
#    And,
#
#    The iCraft team:
#                   <Andrew Caluzzi> tehcid@gmail.com AKA "tehcid"
#                   <Andrew Dolgov> fox@bah.org.ru AKA "gothfox"
#                   <Andrew Horn> Andrew@GJOCommunity.com AKA "AndrewPH"
#                   <Brad Reardon> brad@bradness.co.cc AKA "PixelEater"
#                   <Clay Sweetser> CDBKJmom@aol.com AKA "Varriount"
#                   <James Kirslis> james@helplarge.com AKA "iKJames"
#                   <Jason Sayre> admin@erronjason.com AKA "erronjason"
#                   <Jonathon Dunford> sk8rjwd@yahoo.com AKA "sk8rjwd"
#                   <Joseph Connor> destroyerx100@gmail.com AKA "destroyerx1"
#                   <Kamyla Silva> supdawgyo@hotmail.com AKA "NotMeh"
#                   <Kristjan Gunnarsson> kristjang@ffsn.is AKA "eugo"
#                   <Nathan Coulombe> NathanCoulombe@hotmail.com AKA "Saanix"
#                   <Nick Tolrud> ntolrud@yahoo.com AKA "ntfwc"
#                   <Noel Benzinger> ronnygmod@gmail.com AKA "Dwarfy"
#                   <Randy Lyne> qcksilverdragon@gmail.com AKA "goober"
#                   <Willem van der Ploeg> willempieeploeg@live.nl AKA "willempiee"
#
#    Disclaimer: Parts of this code may have been contributed by the end-users.
#
#    iCraft is licensed under the Creative Commons
#    Attribution-NonCommercial-ShareAlike 3.0 Unported License. 
#    To view a copy of this license, visit http://creativecommons.org/licenses/by-nc-sa/3.0/
#    Or, send a letter to Creative Commons, 171 2nd Street,
#    Suite 300, San Francisco, California, 94105, USA.

lx,ly,lz = x+n,y+m,z+o
if world.blockstore.raw_blocks[world.blockstore.get_offset(lx,ly,lz)] != '1':
    block = '1'
    world[lx, ly, lz] = block
    self.client.queueTask(TASK_BLOCKSET, (lx, ly, lz, block), world=world)
    self.client.sendBlock(lx, ly, lz, block)
for i,j,k in var_sensorblocksoffsets:
    ax,ay,az = x+i,y+j,z+k
    if world.blockstore.raw_blocks[world.blockstore.get_offset(ax,ay,az)] != '\x14':
        block = '\x14'
        world[ax, ay, az] = block
        self.client.queueTask(TASK_BLOCKSET, (ax, ay, az, block), world=world)
        self.client.sendBlock(ax, ay, az, block)
for client in worldblockchangesdict:
    cx,cy,cz,var_timeofchange = worldblockchangesdict[client][0][:4]
    if (cx,cy,cz) == (lx,ly+1,lz) and time()- var_timeofchange < 2:
        if not entity[6]:
            blockset = worldblockchangesdict[client][0][5]
            if blockset == 46:
                worldblockchangedellist.append(client)
                block = '\x00'
                world[lx, ly+1, lz] = block
                self.client.queueTask(TASK_BLOCKSET, (lx, ly+1, lz, block), world=world)
                self.client.sendBlock(lx, ly+1, lz, block)
                client.sendServerMessage("Cannon loaded.")
                entity[6] = True
            else:
                worldblockchangedellist.append(client)
                client.sendServerMessage("Please load this cannon with tnt.")
    for i,j,k in var_sensorblocksoffsets:
        ax,ay,az = x+i,y+j,z+k
        if entity[4] not in entities_childerenlist:
            if (cx,cy,cz) == (ax,ay,az) and time()- var_timeofchange < 2:
                if entity[6]:
                    entity[6] = False
                    worldblockchangedellist.append(client)
                    i = world.entities_childerenlist_index
                    world.entities_childerenlist_index += 1
                    entities_childerenlist.append(i)
                    entity[4] = i
                    px,py,pz,ph,pp = worldblockchangesdict[client][1]
                    distancebetween = ((x+2*n-px)**2+(y+1-py)**2+(z+2*o-pz)**2)**0.5
                    h = math.radians(ph*360.0/256.0)
                    p = math.radians(pp*360.0/256.0)
                    rx,ry,rz = math.sin(h)*math.cos(p),-math.sin(p),-math.cos(h)*math.cos(p)
                    ix,iy,iz = int(round(rx*distancebetween+rx+px)),int(round(ry*distancebetween+ry+py)),int(round(rz*distancebetween+rz+pz))
                    entitylist.append(["cannonball",(rx*distancebetween+2*rx+px,ry*distancebetween+2*ry+py,rz*distancebetween+2*rz+pz),2,2,[rx,ry,rz],i])
                    entitylist.append(["smoke",(ix+1,iy,iz),4,4,True])
                    entitylist.append(["smoke",(ix-1,iy,iz),4,4,True])
                    entitylist.append(["smoke",(ix-1,iy+1,iz),4,4,True])
                else:
                    client.sendServerMessage("Cannon is not loaded.")
                    worldblockchangedellist.append(client)
