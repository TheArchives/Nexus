import os, random
from core.decorators import *
from core.protocol import *
from core.server import *
from core.globals import *

class AwardPlugin(ProtocolPlugin):

    commands = {

        "award": "commandAward",
        "awards": "commandCheckAwards",

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
        "/awards - Guest\nCheck your awards."
        if len(parts) > 1:
            self.client.sendErrorMessage("This command doesn't require parameters.")
        else:
            f = open("config/data/awards.meta", "r")
            self.client.sendServerMessage("Your current awards are:")
            nameLower = self.client.username.lower()
            for line in f:
                if line.startswith(nameLower):
                    self.client.sendSplitServerMessage("%s" % str(line.replace(nameLower, " ")))
