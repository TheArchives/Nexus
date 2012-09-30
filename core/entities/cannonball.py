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

entity[4][1] = entity[4][1] - 0.02
vx,vy,vz = entity[4]
rx,ry,rz = var_position
x,y,z = int(round(rx)),int(round(ry)),int(round(rz))
rx,ry,rz = rx+vx,ry+vy,rz+vz
var_position = rx,ry,rz
cx,cy,cz = int(round(rx)),int(round(ry)),int(round(rz))
var_cango = True
try:
    blocktocheck = ord(world.blockstore.raw_blocks[world.blockstore.get_offset(cx,cy,cz)])
    if blocktocheck != 0:
        var_cango = False
except:
    var_cango = False
if (x,y,z) != (cx,cy,cz):
    hitplayer = False
    for entry in userpositionlist:
        i,j,k = entry[1]
        distance = ((i-x)**2+(j-y)**2+(k-z)**2)**0.5
        if distance < 2:
            hitplayer = True
    if var_cango and not hitplayer:
        block = '\x00'
        world[x, y, z] = block
        self.client.queueTask(TASK_BLOCKSET, (x, y, z, block), world=world)
        self.client.sendBlock(x, y, z, block)
        x,y,z = cx,cy,cz
        block = '1'
        world[x, y, z] = block
        self.client.queueTask(TASK_BLOCKSET, (x, y, z, block), world=world)
        self.client.sendBlock(x, y, z, block)
    else:
        entitylist.append(["tnt",(x,y,z),1,1,True,0,5])
        del entities_childerenlist[entities_childerenlist.index(entity[5])]
        var_dellist.append(index)
        
