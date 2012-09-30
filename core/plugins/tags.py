# The Nexus software is licensed under the BSD 2-Clause license.
#
# You should have recieved a copy of this license with the software.
# If you did not, you can find one at the following link.
#
# http://opensource.org/licenses/bsd-license.php


import cPickle
from core.plugins import ProtocolPlugin
from core.decorators import *

class TitlePlugin(ProtocolPlugin):
    
    commands = {
        "tag":     "commandSetTag",
        "settag":     "commandSetTag",
    }
    
    # System methods, not for commands
    def loadRank(self):
        file = open('config/data/tags.dat', 'r')
        rank_dic = cPickle.load(file)
        file.close()
        return rank_dic
    
    def dumpRank(self, bank_dic):
        file = open('config/data/tags.dat', 'w')
        cPickle.dump(bank_dic, file)
        file.close()
    
    @player_list
    @director_only
    def commandSetTag(self, parts, fromloc, overriderank):
        "/tag [tag] username - Director\nAliases: settag\nGives or removes a tag to username."
        if len(parts)>2:
            rank = self.loadRank()
            user = parts[1].lower()
            rank[user] = (" ".join(parts[2:]))
            self.dumpRank(rank)
            if len(" ".join(parts[2:]))<8:
                self.client.sendServerMessage("Added the tag of: "+(" ".join(parts[2:])))
            else:
                self.client.sendServerMessage("Added the tag of: "+(" ".join(parts[2:])))
        elif len(parts)==2:
            rank = self.loadRank()
            user = parts[1].lower()
            if user not in rank:
                self.client.sendServerMessage("Syntax: /tag tag username")
                return False
            else:
                rank.pop(user)
                self.dumpRank(rank)
                self.client.sendServerMessage("Removed the tag.")
