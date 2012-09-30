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

import shutil, os, sys, subprocess, traceback
from reqs.twisted.internet import reactor
from core.plugins import ProtocolPlugin
from core.decorators import *
from core.constants import *
from core.globals import *

class IsoImage(ProtocolPlugin):

    commands = {
        "isoimage": "commandIso",
    }

    @op_only
    def commandIso(self, parts, fromloc, overriderank):
        "/isoimage [1-4] - Op\nCreates an IsoImage of the current world."
        if len(parts) == 2:
            if str(parts[1]) in "1234":
                angle = parts[1]
            else:
                self.client.sendServerMessage('You must provide 1-4 for the angle.')
                return
        else:
            angle = 1
        world = self.client.world
        pathname = os.getcwd()
        savepath = pathname + "/core/isoimage/images/"
        worldname = world.basename.split("/")[1]
        worldpath = pathname + "/worlds/" + worldname
        try:
            os.chdir(pathname + "/core/isoimage/")
            if checkos() == "Windows":
                os.system('java -Xms512M -Xmx1024M -cp minecraft-server.jar; OrigFormat save "%s" server_level.dat' % worldpath)
                os.system('java -Xms128M -Xmx1024M -cp minecraft-server.jar;IsoCraft++.jar isocraft server_level.dat tileset.png output.png %s -1 -1 -1 -1 -1 -1 visible'%str(angle))
            else:
                os.system('java -Xms512M -Xmx1024M -cp minecraft-server.jar: OrigFormat save "%s" server_level.dat' % worldpath)
                os.system('java -Xms128M -Xmx1024M -cp minecraft-server.jar:IsoCraft++.jar isocraft server_level.dat tileset.png output.png %s -1 -1 -1 -1 -1 -1 visible'%str(angle))
            shutil.move("output.png", "images/%s%s.png" % (worldname, str(angle)))
            os.chdir(pathname)
            self.client.sendServerMessage('Isoimage %s has been created.' %(worldname + str(angle) + ".png"))
        except:
            self.client.sendSplitServerMessage(traceback.format_exc().replace("Traceback (most recent call last):", ""))
            self.client.sendSplitServerMessage("Internal Server Error - Traceback (Please report this to the Server Staff or the iCraft Team, see /about for contact info)")
            self.client.logger.error(traceback.format_exc())
            os.chdir(pathname)
