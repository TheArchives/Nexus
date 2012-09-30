#    iCraft is Copyright 2010 both
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
#                   <Joshua Connor> fooblock@live.com AKA "Fooblock"
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

var_cango = True
try:
    blocktocheck = ord(world.blockstore.raw_blocks[world.blockstore.get_offset(x,y-1,z)])
    if blocktocheck != 0:
        var_cango = False
except:
    var_cango = False
if var_cango:
    block = '\x00'
    world[x, y, z] = block
    self.client.queueTask(TASK_BLOCKSET, (x, y, z, block), world=world)
    self.client.sendBlock(x, y, z, block)
    world[x, y+1, z] = block
    self.client.queueTask(TASK_BLOCKSET, (x, y+1, z, block), world=world)
    self.client.sendBlock(x, y+1, z, block)
    var_position = (x,y-1,z)
    x,y,z = var_position
    block = chr(12)
    world[x, y, z] = block
    self.client.queueTask(TASK_BLOCKSET, (x, y, z, block), world=world)
    self.client.sendBlock(x, y, z, block)
    block = chr(12)
    world[x, y+1, z] = block
    self.client.queueTask(TASK_BLOCKSET, (x, y+1, z, block), world=world)
    self.client.sendBlock(x, y+1, z, block)
else:
    closestposition = (0,0)
    closestclient = None
    closestdistance = None
    for entry in userpositionlist:
        client = entry[0]
        var_pos = entry[1]
        i,j,k = var_pos
        distance = ((i-x)**2+(j-y)**2+(k-z)**2)**0.5
        if closestdistance == None:
            closestdistance = distance
            closestclient = client
            closestposition = (var_pos[0],var_pos[2])
        else:
            if distance < closestdistance:
                closestdistance = distance
                closestclient = client
                closestposition = (var_pos[0],var_pos[2])
    if closestdistance < 3:
        closestclient.sendServerMessage("I'm a fool!")
    if closestdistance < 2:
        sx,sy,sz,sh = world.spawn
        closestclient.teleportTo(sx,sy,sz,sh)
        self.client.sendPlainWorldMessage("&c%s has become a fool." % closestclient.username)
    i,k = closestposition
    distance = ((i-x)**2+(k-z)**2)**0.5
    if distance != 0:
        target = [int((i-x)/(distance/1.75)) + x,y,int((k-z)/(distance/1.75)) + z]
        i,j,k = target
        var_cango = True
        try:
            blocktocheck = ord(world.blockstore.raw_blocks[world.blockstore.get_offset(i,j,k)])
            if blocktocheck != 0:
                var_cango = False
            blocktocheck = ord(world.blockstore.raw_blocks[world.blockstore.get_offset(i,j+1,k)])
            if blocktocheck != 0:
                var_cango = False
        except:
            var_cango = False
        if var_cango:
            block = '\x00'
            world[x, y, z] = block
            self.client.queueTask(TASK_BLOCKSET, (x, y, z, block), world=world)
            self.client.sendBlock(x, y, z, block)
            world[x, y+1, z] = block
            self.client.queueTask(TASK_BLOCKSET, (x, y+1, z, block), world=world)
            self.client.sendBlock(x, y+1, z, block)
            var_position = target
            x,y,z = var_position
            block = chr(12)
            world[x, y, z] = block
            self.client.queueTask(TASK_BLOCKSET, (x, y, z, block), world=world)
            self.client.sendBlock(x, y, z, block)
            block = chr(12)
            world[x, y+1, z] = block
            self.client.queueTask(TASK_BLOCKSET, (x, y+1, z, block), world=world)
            self.client.sendBlock(x, y+1, z, block)
        else:
            var_cango = True
            target[1] = target[1] + 1
            j = target[1]
            try:
                blocktocheck = ord(world.blockstore.raw_blocks[world.blockstore.get_offset(i,j,k)])
                if blocktocheck != 0:
                    var_cango = False
                blocktocheck = ord(world.blockstore.raw_blocks[world.blockstore.get_offset(i,j+1,k)])
                if blocktocheck != 0:
                    var_cango = False
            except:
                var_cango = False
            if var_cango:
                block = '\x00'
                world[x, y, z] = block
                self.client.queueTask(TASK_BLOCKSET, (x, y, z, block), world=world)
                self.client.sendBlock(x, y, z, block)
                world[x, y+1, z] = block
                self.client.queueTask(TASK_BLOCKSET, (x, y+1, z, block), world=world)
                self.client.sendBlock(x, y+1, z, block)
                var_position = target
                x,y,z = var_position
                block = chr(12)
                world[x, y, z] = block
                self.client.queueTask(TASK_BLOCKSET, (x, y, z, block), world=world)
                self.client.sendBlock(x, y, z, block)
                block = chr(12)
                world[x, y+1, z] = block
                self.client.queueTask(TASK_BLOCKSET, (x, y+1, z, block), world=world)
                self.client.sendBlock(x, y+1, z, block)
