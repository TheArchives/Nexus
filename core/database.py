# The Nexus software is licensed under the BSD 2-Clause license.
#
# You should have recieved a copy of this license with the software.
# If you did not, you can find one at the following link.
#
# http://opensource.org/licenses/bsd-license.php


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
