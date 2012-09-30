# The Nexus software is licensed under the BSD 2-Clause license.
#
# You should have recieved a copy of this license with the software.
# If you did not, you can find one at the following link.
#
# http://opensource.org/licenses/bsd-license.php


import cPickle
from core.plugins import ProtocolPlugin
from core.decorators import *
from core.constants import *

class TitlePlugin(ProtocolPlugin):
    
    commands = {
        "title":     "commandSetTitle",
        "settitle":     "commandSetTitle",
        "qtitle":     "commandQuietSetTitle",
        "showtitle":     "commandShowTitle",
    }
    
    # System methods, not for commands
    def loadRank(self):
        file = open('config/data/titles.dat', 'r')
        rank_dic = cPickle.load(file)
        file.close()
        return rank_dic
    
    def dumpRank(self, bank_dic):
        file = open('config/data/titles.dat', 'w')
        cPickle.dump(bank_dic, file)
        file.close()
    
    def setTitle(self, username, title, quiet):
        rank = self.loadRank()
        usernameLower = username.lower()
        if len(title) > 0 :
            rank[usernameLower] = (title)
            self.dumpRank(rank)
            if len(title) > 7 :
                self.client.sendServerMessage("NOTICE: We recommend for you to keep Titles under 7 chars.")
            self.client.sendServerMessage("Added the title of: "+(title))
            if not quiet:
                user = self.client.findUserExact(usernameLower)
                if user is not None:
                    user.sendServerMessage(("%s changed your title to: " % self.client.username)+(title))
        else:
            if usernameLower not in rank:
                self.client.sendServerMessage("Syntax: /title username title")
                #return False
            else:
                rank.pop(usernameLower)
                self.dumpRank(rank)
                self.client.sendServerMessage("Removed the title.")
                if not quiet:
                    user = self.client.findUserExact(usernameLower)
                    if user is not None:
                        user.sendServerMessage("%s removed your title." % self.client.username)
    
    @player_list
    @director_only
    def commandSetTitle(self, parts, fromloc, overriderank):
        "/title username [title] - Director\nAliases: settitle\nGives or removes a title to username."
        if len(parts)>2:
            self.setTitle(parts[1], " ".join(parts[2:]), False)
        elif len(parts)==2:
            self.setTitle(parts[1], "", False)
        else:
            self.client.sendServerMessage("Please specify a username.")
                
    @director_only
    def commandQuietSetTitle(self, parts, fromloc, overriderank):
        "/qtitle username [title] - Director\nGives or removes a title to username, without notifying them."
        if len(parts)>2:
            self.setTitle(parts[1], " ".join(parts[2:]), True)
        elif len(parts)==2:
            self.setTitle(parts[1], "", True)
        else:
            self.client.sendServerMessage("Please specify a username.")
    
    @player_list
    @director_only
    def commandShowTitle(self, parts, fromloc, overriderank):
        "/showtitle username - Director\nShows the users current title."
        if len(parts)==2:
            rank = self.loadRank()
            name = parts[1].lower()
            if name in rank:
                title = rank[name] + " "
                
                if self.client.factory.isSpectator(name):
                    color = COLOUR_BLACK
                elif self.client.factory.isServerOwner(name):
                    color = COLOUR_DARKRED
                elif self.client.factory.isDirector(name):
                    color = COLOUR_GREEN
                elif self.client.factory.isCoder(name):
                    color = COLOUR_DARKPURPLE
                elif self.client.factory.isAdmin(name):
                    color = COLOUR_RED
                elif self.client.factory.isMod(name):
                    color = COLOUR_BLUE
                elif self.client.factory.isMember(name):
                    color = COLOUR_GREY
                else:
                    color = COLOUR_WHITE
                
                self.client.sendServerMessage("Title: " + color + title + name)
            else:
                self.client.sendServerMessage(name + " does not have a title.")
        else:
            self.client.sendServerMessage("Please specify a username.")