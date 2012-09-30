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
#    The RainbowPlugin Team:
#                   <Brian Hansen> jabawakijadehawk@gmail.com AKA "blahblahbal"
#                   <CENSORED> @Contact techdude59 through the above email@ AKA "techdude59"
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

class RainbowPlugin(ProtocolPlugin):
    commands = {
        "rainbow": "commandRainbow",
        "fabulous": "commandRainbow",
        "fab": "commandRainbow",
        "mefab": "commandMeRainbow",
        "merainbow": "commandMeRainbow",
    }

    colors = ["&4", "&c", "&e", "&a", "&2", "&3", "&b", "&d", "&5"]

    @op_only
    def commandRainbow(self, parts, fromloc, overriderank):
        "/rainbow - Guest\nAliases: fabulous, fab\nMakes your text rainbow."
        if len(parts) == 1:
            self.client.sendServerMessage("Please include a message to rainbowify.")
        else:
            stringInput = parts[1:]
            input  = ""
            for a in stringInput:
                input = input + a + " "
            output = ""
            colorNum = 0
            for x in input:
                if x != " ":
                    output = output + colors[colorNum] + x
                    colorNum = colorNum + 1
                    if colorNum >= 9:
                        colorNum = 0
                if x == " ":
                    output = output + x
            self.client.factory.queue.put((self.client, TASK_INGAMEMESSAGE, " "+self.client.userColour()+self.client.username+": "+output))

    @op_only
    def commandMeRainbow(self, parts, fromloc, overriderank):
        "/mefab - Guest\nAliases: merainbow\nSends an action in rainbow colors."
        if len(parts) == 1:
            self.client.sendServerMessage("Please include an action to rainbowify.")
        else:
            stringInput = parts[1:]
            input  = ""
            for a in stringInput:
                input = input + a + " "
            output = ""
            colorNum = 0
            for x in input:
                if x != " ":
                    output = output + colors[colorNum] + x
                    colorNum = colorNum + 1
                    if colorNum >= 9:
                        colorNum = 0
                if x == " ":
                    output = output + x       
            self.client.factory.queue.put((self.client, TASK_INGAMEMESSAGE, "* "+self.client.userColour()+self.client.username+": "+output))
