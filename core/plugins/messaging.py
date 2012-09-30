# The Nexus software is licensed under the BSD 2-Clause license.
#
# You should have recieved a copy of this license with the software.
# If you did not, you can find one at the following link.
#
# http://opensource.org/licenses/bsd-license.php


import random
from core.plugins import ProtocolPlugin
from core.decorators import *
from core.constants import *

class MessagingPlugin(ProtocolPlugin):
    
    commands = {
        "say": "commandSay",
        "msg": "commandSay",
        "me": "commandMe",
        "srb": "commandSRB",
        "srs": "commandSRS",
        "u": "commandUrgent",
        "urgent": "commandUrgent",
        "ss": "commandss",
        "om": "commandnom",
        "away": "commandAway",
        "afk": "commandAway",
        "brb": "commandAway",
        "back": "commandBack",
        "slap": "commandSlap",
        "smcak": "commandSmcak",
        "smack": "commandSmack",
        "pwn": "commandPwn",
        "kill": "commandKill",
        "grim": "commandGrim",
        "ex": "commandEx",
        "eat": "commandEat",
        "!": "commandEx",
        "mkill": "commandMassKill",
        "reverse": "commandReverse",
        "rev": "commandReverse",
        "smite": "commandSmite",
        "award": "commandAward",
        "awards": "commandCheckAwards",
        #"you": "commandYou",
    }

    @mod_only
    def commandAward(self, parts, fromloc, overriderank):
        "/award username awardname - Mod\nAward a user!"
        if len(parts) < 3:
            self.client.sendServerMessage("Please include a username and an award.")
        else:
            if parts[1].lower() == self.client.username.lower():
                self.client.sendServerMessage("You can't award yourself!")
            else:
                award = str(parts[2:])
                award2 = award.replace("[", "")
                award3 = award2.replace("]", "")
                award4 = award3.replace(",", "")
                award5 = award4.replace("'", "")
                self.client.factory.addAward(str(parts[2:]), parts[1].lower())
                self.client.factory.queue.put((self.client, TASK_AWARD, "[AWARD] %s has been given a %s award!" % (parts[1], award5)))

    def commandCheckAwards(self, parts, fromloc, overriderank):
        "/awards [page] - Guest\nCheck your awards."
        if len(parts) > 2:
            self.client.sendErrorMessage("Please include either nothing or just a page number.")
        else:
            if len(parts) == 2:
                try:
                    page = int(parts[1])
                except ValueError:
                    self.client.sendServerMessage("Page must be a Number.")
                    return
            else:
                page = 1
        
            awardlist = []
            f = open("config/data/awards.meta", "r")
            nameLower = self.client.username.lower()
            for line in f:
                if line.startswith(nameLower):
                    awardlist.append(line.replace(nameLower, " "))
            self.client.sendServerPagedList("Your awards are:", awardlist, page)

    @admin_only
    def commandReverse(self, parts, fromloc, overriderank):
        "/reverse <message> - Admin\nAliases: rev\nReverses your text."
        if len(parts) < 2:
            self.client.sendServerMessage("Please include a message to reverse.")
        else:
            stringInput = parts[1:]
            input = ""
            for a in stringInput:
                input = input + a + " "
            output = ""
            for x in input:
                if x != " ":
                    output = output + x
                if x == " ":
                    output = output + x
            self.client.factory.queue.put((self.client, TASK_GREEN, " "+self.client.userColour()+self.client.username+": "+COLOUR_WHITE+output[::-1]))

    @player_list
    @unsilenced_only
    def commandBack(self, parts, fromloc, overriderank):
        "/back - Guest\nPrints out message of you coming back."
        if fromloc == "user":
            if len(parts) != 1:
                self.client.sendServerMessage("This command doesn't need arguments")
            else:
                if self.client.gone != 1:
                    self.client.sendServerMessage("You haven't gone away!")
                else:
                    self.client.factory.queue.put((self.client, TASK_AWAYMESSAGE, self.client.username + " is now: Back."))
                    self.client.gone = 0
                    self.client.resetIdleTimer()
    
    @player_list
    @unsilenced_only
    def commandAway(self, parts, fromloc, overriderank):
        "/away reason - Guest\nAliases: afk, brb\nPrints out message of you going away."
        if fromloc == "user":
            if self.client.gone == 1:
                self.client.sendServerMessage("You are already away!")
            else:
                if len(parts) == 1:
                    self.client.factory.queue.put((self.client, TASK_AWAYMESSAGE, self.client.username + " has gone: Away."))
                else:
                    self.client.factory.queue.put((self.client, TASK_AWAYMESSAGE, self.client.username + " has gone: "+(" ".join(parts[1:]))))
            self.client.gone = 1
            self.client.resetIdleTimer()

    @player_list
    @unsilenced_only
    def commandMe(self, parts, fromloc, overriderank):
        "/me action - Guest\nPrints 'username action'"
        if fromloc == "user":
            if len(parts) == 1:
                self.client.sendServerMessage("Please type an action.")
            else:
                self.client.factory.queue.put((self.client, TASK_ACTION, (self.client.id, self.client.userColour(), self.client.username, " ".join(parts[1:]))))
    
    @mod_only
    def commandSay(self, parts, fromloc, overriderank):
        "/say message - Mod\nAliases: msg\nPrints out message in the server color."
        if len(parts) == 1:
            self.client.sendServerMessage("Please type a message.")
        else:
            self.client.factory.queue.put((self.client, TASK_SERVERMESSAGE, ("[MSG] "+(" ".join(parts[1:])))))

    @coder_only
    def commandEx(self, parts, fromloc, overriderank):
        "/ex message - Coder\nPrints out an exclamation."
        if len(parts) == 1:
            self.client.sendServerMessage("Please type a message.")
        else:
            self.client.factory.queue.put((self.client, TASK_GREEN, ("[EXCLAMATION] "+(" ".join(parts[1:])))))

    @coder_only
    def commandGrim(self, parts, fromloc, overriderank):
        "/grim message - Coder\nPrints out a grim message."
        if len(parts) == 1:
            self.client.sendServerMessage("Please type a message.")
        else:
            self.client.factory.queue.put((self.client, TASK_BLACK, ("[GRIM] "+(" ".join(parts[1:])))))
    
    @director_only
    def commandSRB(self, parts, fromloc, overriderank):
        "/srb [reason] - Director\nPrints out a reboot message."
        if len(parts) == 1:
            self.client.factory.queue.put((self.client, TASK_SERVERURGENTMESSAGE, ("[Server Reboot] Be back in a few.")))
        else:
            self.client.factory.queue.put((self.client, TASK_SERVERURGENTMESSAGE, ("[Server Reboot] "+(" ".join(parts[1:])))))

    @director_only
    def commandSRS(self, parts, fromloc, overriderank):
        "/srs [reason] - Director\nPrints out a shutdown message."
        if len(parts) == 1:
            self.client.factory.queue.put((self.client, TASK_SERVERURGENTMESSAGE, ("[Server Shutdown] See you later.")))
        else:
            self.client.factory.queue.put((self.client, TASK_SERVERURGENTMESSAGE, ("[Server Shutdown] "+(" ".join(parts[1:])))))

    @admin_only
    def commandUrgent(self, parts, fromloc, overriderank):
        "/u message - Admin\nAliases: urgent\nPrints out message in the server color."
        if len(parts) == 1:
            self.client.sendServerMessage("Please type a message.")
        else:
            self.client.factory.queue.put((self.client, TASK_SERVERURGENTMESSAGE, "[Urgent] "+(" ".join(parts[1:]))))

    @director_only
    def commandss(self, parts, fromloc, overriderank):
        "/ss message - Director\nPrints out message in the server color."
        if len(parts) == 1:
            self.client.sendServerMessage("Please type a message.")
        else:
            self.client.factory.queue.put((self.client, TASK_INGAMEMESSAGE, " ".join(parts[1:])))

    @owner_only
    def commandnom(self, parts, fromloc, overriderank):
        "/om message - Owner\nAliases: urgent\nPrints out a message."
        if len(parts) == 1:
            self.client.sendServerMessage("Please type a message.")
        else:
            self.client.factory.queue.put((self.client, TASK_OWNERMESSAGE, " ".join(parts[1:])))

    @mod_only
    def commandEat(self, parts, fromloc, overriderank):
        "/eat entry - Mod/nEats something."
        if len(parts) == 1:
            self.client.sendServerMessage("Please include a noun to eat")
        elif (parts[1]).lower() == "god":
            self.client.sendServerMessage("You can't eat God, sorry.")
        elif (parts[1]).lower() == "chuck" and (parts[2]).lower() == "norris":
            self.client.factory.queue.put((self.client, TASK_INGAMEMESSAGE, "* "+"&d"+self.client.username+" has been eaten by Chuck Norris!"))
        elif (parts[1]) == self.client.username:
            self.client.factory.queue.put((self.client, TASK_INGAMEMESSAGE, "* "+"&d"+self.client.username+" has been eaten by themself!"))
        else:
            self.client.factory.queue.put((self.client, TASK_INGAMEMESSAGE, "* "+"&d"+self.client.username+" has eaten "+(" ".join(parts[1:]))))

    @player_list
    @unsilenced_only
    def commandSlap(self, parts, fromloc, overriderank):
        "/slap username [with object] - Guest\nSlap username [with object]."
        if len(parts) == 1:
            self.client.sendServerMessage("Enter the name for the slappee")
        else:
            stage = 0
            name = ''
            object = ''
        for i in range(1, len(parts)):
            if parts[i] == "with":
                stage = 1
                continue
            if stage == 0 : 
                name += parts[i]
                if (i+1 != len(parts) ) : 
                    if ( parts[i+1] != "with" ) : name += " "
            else:
                object += parts[i]
                if ( i != len(parts) - 1 ) : object += " "
        else:
            # Make sure they've input an actual username before trying to affect it.
            if parts[1] in self.client.factory.usernames :
                x, y, z, h, p = self.client.factory.usernames[parts[1]].x>>5, self.client.factory.usernames[parts[1]].y>>5, self.client.factory.usernames[parts[1]].z>>5, self.client.factory.usernames[parts[1]].h, self.client.factory.usernames[parts[1]].p
                self.client.factory.usernames[parts[1]].teleportTo(x+2, y+1, z, h, p)

            if stage == 1:
                self.client.factory.queue.put((self.client, TASK_INGAMEMESSAGE, "* &d%s slaps %s with %s!" % (self.client.username,name,object)))
            else:
                self.client.factory.queue.put((self.client, TASK_INGAMEMESSAGE, "* &d%s slaps %s with a giant smelly trout!" % (self.client.username,name)))

    @player_list
    @unsilenced_only
    def commandSmcak(self, parts, fromloc, overriderank):
        "/smcak username - Guest\nAliases: smack\nSmcaks username."
        if len(parts) == 1:
            self.client.factory.queue.put((self.client, TASK_SERVERMESSAGE, "%s smcaked themself!" % (self.client.username)))
        else:
            name = parts[1]
            if name == self.client.username or name == "self":
                self.client.factory.queue.put((self.client, TASK_SERVERMESSAGE, "%s smcaked themself!" % (self.client.username)))
            else:
                self.client.factory.queue.put((self.client, TASK_SERVERMESSAGE, "%s was smcaked!" % (name)))

    @player_list
    @unsilenced_only
    def commandSmack(self, parts, fromloc, overriderank):
        "/smack username - Guest\nAliases: smcak\nSmacks username."
        if len(parts) == 1:
            self.client.sendServerMessage("Please enter a username to smack.")
        else:
            self.client.factory.queue.put((self.client, TASK_SERVERMESSAGE, "%s failed at smcaking!!" % (self.client.username)))
    
    @unsilenced_only
    def commandPwn(self, parts, fromloc, overriderank):
        "/pwn name - admin\nPwns the given name."
        if len(parts) == 1:
            self.client.sendServerMessage("Please enter a name for the pwnee.")
        elif (parts[1]) == self.client.username:
            self.client.factory.queue.put((self.client, TASK_SERVERURGENTMESSAGE, ""+self.client.username+" has pwned themself!"))
        elif (parts[1]).lower() == "chuck" and (parts[2]).lower() == "norris":
            self.client.factory.queue.put((self.client, TASK_SERVERURGENTMESSAGE, "Chuck Norris has pwned "+self.client.username+"!"))
        else:
            self.client.factory.queue.put((self.client, TASK_SERVERURGENTMESSAGE, (" ".join(parts[1:]))+" has been pwned by "+self.client.username+"!"))

    @mod_only
    @only_partialusername_command
    def commandKill(self, username, fromloc, overriderank):
        "/kill username [reason] - Mod\nKills the user for reason (optional)"        
        killer = self.client.username                           
        if username in INFO_VIPLIST:
           self.client.sendServerMessage("You can't kill awesome people, sorry.")
        elif username == "theundeadfish":
           self.client.sendServerMessage("But he's already dead.")
        else:
            if username in self.client.factory.usernames:
                self.client.factory.usernames[username].teleportTo(self.client.factory.usernames[username].world.spawn[0], self.client.factory.usernames[username].world.spawn[1], self.client.factory.usernames[username].world.spawn[2], self.client.factory.usernames[username].world.spawn[3])
                self.client.factory.usernames[username].sendServerMessage("You have been killed by %s." % self.client.username)
                self.client.factory.queue.put((self.client, TASK_SERVERURGENTMESSAGE, username +" has been killed by " + killer))
                #if params:     #TODO change the function to accept params for a kill reason
                #    self.client.factory.queue.put((self.client, TASK_SERVERURGENTMESSAGE, "Reason: "+(" ".join(params))))
            else:
                self.client.sendServerMessage("%s is not on the server." % username)

    @player_list
    @director_only
    def commandMassKill(self, parts, fromloc, overriderank):
        "/mkill - Director\nKills all users on the server."
        for user in self.client.factory.usernames:
            self.client.factory.usernames[user].teleportTo(self.client.factory.usernames[user].world.spawn[0], self.client.factory.usernames[user].world.spawn[1], self.client.factory.usernames[user].world.spawn[2], self.client.factory.usernames[user].world.spawn[3])
        self.client.factory.queue.put((self.client, TASK_SERVERURGENTMESSAGE, "[MASSKILL] Everyone has been killed."))

    @admin_only
    @username_command
    def commandSmite(self, user, fromloc, overriderank, params=[]):
        "/smite username [reason] - Admin\nSmites the user for reason (optional)"        
        smiter = self.client.username
        user.teleportTo(user.world.spawn[0], user.world.spawn[1], user.world.spawn[2], user.world.spawn[3])
        user.sendServerMessage("You have been smited by %s." % self.client.username)
        text = user.username + " has been smited by " + smiter
        if params:
            text += ". Reason: " + (" ".join(params))
            #self.client.factory.queue.put((self.client, TASK_CYAN, "Reason: " + (" ".join(params))))
        self.client.factory.queue.put((self.client, TASK_CYAN, text))


    """@mod_only
    def commandYou(self, parts, fromloc, overriderank):
        "/you user message - Mod\nSends a /me for user."
        if len(parts) < 3:
            self.client.sendServerMessage("Please include a username and a message.")
        else:
            color = self.client.factory.usernames[parts[1]].userColour()
            user = parts[1]
            msg = str(parts[2:])
            msg = msg.replace("[", "")
            msg = msg.replace("]", "")
            msg = msg.replace(",", "")
            msg = msg.replace("'", "")
            self.client.factory.queue.put((self.client, TASK_INGAMEMESSAGE, "* %s%s %s%s" % (color, user, COLOUR_WHITE, msg)))"""
