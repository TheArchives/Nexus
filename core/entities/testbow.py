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
