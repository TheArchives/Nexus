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

import traceback, cPickle
from core.plugins import ProtocolPlugin
from core.decorators import *
from reqs.twisted.internet import reactor
from core.constants import *

class OfflineMessPlugin(ProtocolPlugin):
    
    commands = {
          "s": "commandSendMessage",
          "sendmessage": "commandSendMessage",
          "inbox": "commandCheckMessages",
          "c": "commandClear",
          "clear": "commandClear",
    }
        
    def commandSendMessage(self,parts, fromloc, overriderank):
        "/s username message - Guest\nAliases: sendmessage\nSends an message to the users Inbox."
        if len(parts) < 3:
            self.client.sendServerMessage("You must provide a username and a message.")
        else:
            try:
                from_user = self.client.username.lower()
                to_user = parts[1].lower()
                mess = " ".join(parts[2:])
                file = open('config/data/inbox.dat', 'r')
                messages = cPickle.load(file)
                file.close()
                if to_user in messages:
                    messages[to_user]+= "\n" + from_user + ": " + mess
                else:
                    messages[to_user] = from_user + ": " + mess
                file = open('config/data/inbox.dat', 'w')
                cPickle.dump(messages, file)
                file.close()
                self.client.factory.usernames[to_user].MessageAlert()
                self.client.sendServerMessage("A message has been sent to %s." % to_user)
            except:
                self.client.sendServerMessage("Error sending message.")

    def commandCheckMessages(self, parts, fromloc, overriderank):
        "/inbox - Guest\nChecks your Inbox of messages"
        file = open('config/data/inbox.dat', 'r')
        messages = cPickle.load(file)
        file.close()
        if self.client.username.lower() in messages:
            self.client._sendMessage(COLOUR_DARKPURPLE, messages[self.client.username.lower()])
            self.client.sendServerMessage("NOTE: Might want to do /c now.")
        else:
            self.client.sendServerMessage("You do not have any messages.")

    def commandClear(self,parts, fromloc, overriderank):
        "/c - Guest\nAliases: clear\nClears your Inbox of messages"
        target = self.client.username.lower()
        file = open('config/data/inbox.dat', 'r')
        messages = cPickle.load(file)
        file.close()
        if len(parts) == 2:
            target = parts[1]
        elif self.client.username.lower() not in messages:
            self.client.sendServerMessage("You have no messages to clear.")
            return False
        messages.pop(target)
        file = open('config/data/inbox.dat', 'w')
        cPickle.dump(messages, file)
        file.close()
        self.client.sendServerMessage("All your messages have been deleted.")
