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

explosionblocklist = [[-3, -1, 0], [-3, 0, -1], [-3, 0, 0], [-3, 0, 1], [-3, 1, 0], [-2, -2, -1], [-2, -2, 0], [-2, -2, 1], [-2, -1, -2], [-2, -1, -1], [-2, -1, 0], [-2, -1, 1], [-2, -1, 2], [-2, 0, -2], [-2, 0, -1], [-2, 0, 0], [-2, 0, 1], [-2, 0, 2], [-2, 1, -2], [-2, 1, -1], [-2, 1, 0], [-2, 1, 1], [-2, 1, 2], [-2, 2, -1], [-2, 2, 0], [-2, 2, 1], [-1, -3, 0], [-1, -2, -2], [-1, -2, -1], [-1, -2, 0], [-1, -2, 1], [-1, -2, 2], [-1, -1, -2], [-1, -1, -1], [-1, -1, 0], [-1, -1, 1], [-1, -1, 2], [-1, 0, -3], [-1, 0, -2], [-1, 0, -1], [-1, 0, 0], [-1, 0, 1], [-1, 0, 2], [-1, 0, 3], [-1, 1, -2], [-1, 1, -1], [-1, 1, 0], [-1, 1, 1], [-1, 1, 2], [-1, 2, -2], [-1, 2, -1], [-1, 2, 0], [-1, 2, 1], [-1, 2, 2], [-1, 3, 0], [0, -3, -1], [0, -3, 0], [0, -3, 1], [0, -2, -2], [0, -2, -1], [0, -2, 0], [0, -2, 1], [0, -2, 2], [0, -1, -3], [0, -1, -2], [0, -1, -1], [0, -1, 0], [0, -1, 1], [0, -1, 2], [0, -1, 3], [0, 0, -3], [0, 0, -2], [0, 0, -1], [0, 0, 1], [0, 0, 2], [0, 0, 3], [0, 1, -3], [0, 1, -2], [0, 1, -1], [0, 1, 0], [0, 1, 1], [0, 1, 2], [0, 1, 3], [0, 2, -2], [0, 2, -1], [0, 2, 0], [0, 2, 1], [0, 2, 2], [0, 3, -1], [0, 3, 0], [0, 3, 1], [1, -3, 0], [1, -2, -2], [1, -2, -1], [1, -2, 0], [1, -2, 1], [1, -2, 2], [1, -1, -2], [1, -1, -1], [1, -1, 0], [1, -1, 1], [1, -1, 2], [1, 0, -3], [1, 0, -2], [1, 0, -1], [1, 0, 0], [1, 0, 1], [1, 0, 2], [1, 0, 3], [1, 1, -2], [1, 1, -1], [1, 1, 0], [1, 1, 1], [1, 1, 2], [1, 2, -2], [1, 2, -1], [1, 2, 0], [1, 2, 1], [1, 2, 2], [1, 3, 0], [2, -2, -1], [2, -2, 0], [2, -2, 1], [2, -1, -2], [2, -1, -1], [2, -1, 0], [2, -1, 1], [2, -1, 2], [2, 0, -2], [2, 0, -1], [2, 0, 0], [2, 0, 1], [2, 0, 2], [2, 1, -2], [2, 1, -1], [2, 1, 0], [2, 1, 1], [2, 1, 2], [2, 2, -1], [2, 2, 0], [2, 2, 1], [3, -1, 0], [3, 0, -1], [3, 0, 0], [3, 0, 1], [3, 1, 0]]
maxentitiystepsatonetime = 20
twoblockhighentities = ["creeper","zombie","noob","person"]
twoblockhighshootingentities = ["bckchngdetector","testbow","paintballgun"]
entityblocklist = {"zombie":[(0,0,0),(0,1,0)],"creeper":[(0,0,0),(0,1,0)],"person":[(0,0,0),(0,1,0)],"noob":[(0,0,0),(0,1,0)],"bckchngdetector":[(0,0,0),(0,1,0)],"testbow":[(0,0,0),(0,1,0)],"paintballgun":[(0,0,0),(0,1,0)]}
colorblocks = [21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36]
var_unpainablelist = [7,20,42,41,49,40,44,43,39,38,6,37,38]
var_unbreakables = ['\x07', '*', ')', '.', '1']
var_childrenentities = ["testarrow","paintball","cannonball"]
unselectableentities = ["testarrow","paintball","cannonball","bckchngdetector","entity1","passiveblob","petblob","smoke","rain","testarrow"]
