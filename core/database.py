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

import apsw, traceback
from collections import deque
from threading import Thread

class connection(Thread):
    "Creates a connenction to the database for storage."

    def __init__(self, world):
        self.run = True
        self.count = 0
        self.path = world.basename+"/storage.db"
        self.memcon = apsw.Connection(":memory:")
        self.memcursor = self.memcon.cursor()
        self.memlist = deque()
        self.worldlist = deque()
        self.worldcon = apsw.Connection("{0}".format(self.path))
        self.worldcursor = self.worldcon.cursor()
        self.worldcursor.execute("pragma journal_mode=wal")
        try:
            self.memcursor.execute("CREATE TABLE blocks (id INTEGER PRIMARY KEY, name VARCHAR(50), date DATE, before INTEGER, after INTEGER)")
            self.worldcursor.execute("CREATE TABLE blocks (id INTEGER PRIMARY KEY, name VARCHAR(50), date DATE, before INTEGER, after INTEGER)")
        except:
            pass

    def opentable(self):
        self.memcursor = None
        self.worldcursor = None
        self.memcon.backup("blocks", self.worldcon, "blocks").step()
        self.memcursor = self.memcon.cursor()
        self.worldcursor = self.worldcon.cursor()

    def close(self):
        self.memwrite()
        self.worldwrite()
        self.memcursor = None
        self.worldcursor = None
        self.run = False

    def writetable(self, blockoffset, name, date, before, after):
        if self.run:
            self.memlist.append((blockoffset, name, date, before, after))
            self.worldlist.append((blockoffset, name, date, before, after))
            if len(self.memlist) > 200:
                self.memwrite()
                self.count = self.count+1
                if self.count > 5:
                    self.worldwrite()

    def memwrite(self):
        if self.run:
            self.memcursor.executemany("INSERT OR REPLACE INTO blocks VALUES (?, ?, ?, ?, ?)", self.worldlist)
            self.memlist.clear()

    def worldwrite(self):
        if self.run:
            self.worldcursor.executemany("INSERT OR REPLACE INTO blocks VALUES (?, ?, ?, ?, ?)", self.worldlist)
            self.worldlist.clear()
            self.count = 0

    def readd(self, entry, column):
        returncolumn = "id, name, date, before, after"
        if len(self.memlist) > 0:
            self.memwrite()
        if isinstance(entry, (int, str)):
            string = "select * from blocks as blocks where {0} = ?".format(column)
            self.memcursor.execute(string, [entry])
            memall = self.memcursor.fetchall()
            if len(memall) == 1:
                memall = memall[0]
            return(memall)
        elif isinstance(entry, (tuple, list)):
            string = 'select * from main as main where {0} in ({1})'.format(column, ('?, '*len(entry))[:-1])
            self.memcursor.execute(string, entry)
            memall = self.memcursor.fetchall()
            return(memall)
        else:
            print traceback.format_exc()
            print ("ERROR - Please make sure your input is correct, dumping information...")
            print ("Entry: %s | Column: %s | Return Column: %s | String: %s" (entry, column, returncolumn, string))
