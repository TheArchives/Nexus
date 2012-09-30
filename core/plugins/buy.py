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
#
#import cPickle
#from core.plugins import ProtocolPlugin
#from core.decorators import *
#from core.constants import *
#from core.globals import *
#
#class BuyPlugin(ProtocolPlugin):
#    
#    commands = {
#        "buy": "commandBuy",
#    }
#    
#    def commandBuy(self, parts, fromloc, overriderank):
#        "/buy worldname size - Guest\nsmall - 64x64x64, 2000 Minecash.\nnormal - 128x128x128, 4000 Minecash.\nMakes a new world, and boots it, if the user has enough money."
#        if len(parts) == 1:
#            self.client.sendServerMessage("Please specify a new worldname and size.")
#        elif self.client.factory.world_exists(parts[1]):
#            self.client.sendServerMessage("Worldname in use")
#        else:
#            if len(parts) == 3 or len(parts) == 4:
#                size = parts[2].lower()
#                if size == "small":
#                    template = "small"
#                    price = 2000
#                elif size == "normal":
#                    template = "normal"
#                    price = 4000
#                else:
#                    self.client.sendServerMessage("%s is not a valid size." % size)
#                    return
#            else:
#                self.client.sendServerMessage("Please specify a worldname and size.")
#                return
#            file = open('config/data/balances.dat', 'r')
#            bank = cPickle.load(file)
#            file.close()
#            amount = price
#            user = self.client.username.lower()
#            if user not in bank:
#                self.client.sendServerMessage("You don't have an account yet. Use /bank first.")
#                return
#            if not amount <= bank[user]:
#                self.client.sendServerMessage("You need atleast %s to buy this world." % amount)
#                return False
#            else:
#                file = open('config/data/balances.dat', 'w')
#                bank[user] = bank[self.client.username.lower()] - amount
#                cPickle.dump(bank, file)
#                file.close()
#                self.client.sendServerMessage("Paid %s for the world." % amount)
#            world_id = parts[1].lower()
#            self.client.factory.newWorld(world_id, template)
#            self.client.factory.loadWorld("worlds/%s" % world_id, world_id)
#            self.client.factory.worlds[world_id].all_write = False
#            if len(parts) < 4:
#                self.client.sendServerMessage("World '%s' made and booted." % world_id)
#                self.client.changeToWorld(world_id)
#                self.client.sendServerMessage(Rank(self, ["/rank", "worldowner", self.client.username, world_id], fromloc, True))
#            world = self.client.factory.worlds[world_id]
#            world.all_write = False
#
