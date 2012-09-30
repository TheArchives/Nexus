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

var_cango = False
var_open = False
closestposition = (0,0)
closestclient = None
closestdistance = None
if entity[5] == True:
    try:
        blocktocheck = ord(world.blockstore.raw_blocks[world.blockstore.get_offset(x,y,z)])
        entity[4] = blocktocheck
        entity[5] = False
    except:
        blocktocheck = ord(world.blockstore.raw_blocks[world.blockstore.get_offset(x,y,z)])
        entity[4] = blocktocheck
for entry in userpositionlist:
    client = entry[0]
    var_pos = entry[1]
    i,j,k = var_pos
    xd = i-x
    yd = j-y
    zd = k-z
    distance = math.sqrt((xd*xd + yd*yd + zd*zd))
    if distance < 4:
        var_open = True
if var_open:
    block = entity[4]
    self.client.queueTask(TASK_BLOCKSET, (x,y,z, block), world=world)
    self.client.sendBlock(x,y,z, block) 
else:
    blocktocheck = ord(world.blockstore.raw_blocks[world.blockstore.get_offset(x,y,z)])
    if blocktocheck == entity[4] or chr(0):
        var_cango = True
if var_cango == True:
    block = 0
    self.client.queueTask(TASK_BLOCKSET, (x,y,z, block), world=world)
    self.client.sendBlock(x,y,z, block)
