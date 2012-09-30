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

from core.plugins import ProtocolPlugin
from core.decorators import *
from core.constants import *
from core.globals import *

class ModsPlugin(ProtocolPlugin):
    
    commands = {
        "staff": "commandStaff",
        "globalbuilders": "commandGlobalBuilders",
        "members": "commandMembers",
        "directors": "commandDirectors",
        "coders": "commandCoders",
        "admins": "commandAdmins",
        "mods": "commandMods",
    }

    @info_list
    def commandStaff(self, parts, fromloc, overriderank):
        "/staff - Guest\nLists all server staff."
        self.client.sendServerMessage("The Server Staff - Owner: "+self.client.factory.owner)
        list = Staff(self)
        for each in list:
            self.client.sendServerList(each)

    @info_list
    def commandGlobalBuilders(self, parts, fromloc, overriderank):
        "/globalbuilders - Guest\nLists all Global Builders."
        if len(self.client.factory.globalbuilders):
            self.client.sendServerList(["Global Builders:"] + list(self.client.factory.globalbuilders))
        else:
            self.client.sendServerList(["Global Builders:"] + list("N/A"))

    @info_list
    def commandMembers(self, parts, fromloc, overriderank):
        "/members - Guest\nLists all Members."
        if len(self.client.factory.members):
            self.client.sendServerList(["Members:"] + list(self.client.factory.members))
        else:
            self.client.sendServerList(["Members:"] + list("N/A"))

    @info_list
    def commandDirectors(self, parts, fromloc, overriderank):
        "/directors - Guest\nLists all Directors."
        if len(self.client.factory.directors):
            self.client.sendServerList(["Directors:"] + list(self.client.factory.directors))
        else:
            self.client.sendServerList(["Directors:"] + list("N/A"))

    @info_list
    def commandCoders(self, parts, fromloc, overriderank):
        "/coders - Guest\nLists all Coders."
        if len(self.client.factory.coders):
            self.client.sendServerList(["Coders:"] + list(self.client.factory.coders))
        else:
            self.client.sendServerList(["Coders:"] + list("N/A"))

    @info_list
    def commandAdmins(self, parts, fromloc, overriderank):
        "/admins - Guest\nLists all Admins."
        if len(self.client.factory.admins):
            self.client.sendServerList(["Admins:"] + list(self.client.factory.admins))
        else:
            self.client.sendServerList(["Admins:"] + list("N/A"))

    @info_list
    def commandMods(self, parts, fromloc, overriderank):
        "/mods - Guest\nLists all Mods."
        if len(self.client.factory.mods):
            self.client.sendServerList(["Mods:"] + list(self.client.factory.mods))
        else:
            self.client.sendServerList(["Mods:"] + list("N/A"))
