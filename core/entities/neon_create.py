# The Nexus software is licensed under the BSD 2-Clause license.
#
# You should have recieved a copy of this license with the software.
# If you did not, you can find one at the following link.
#
# http://opensource.org/licenses/bsd-license.php


color = self.var_entityparts[0]
colorlist = []
if color == "blue":
    c1,c2,c3,c4,c5 = ['\x1b', '\x1c', '\x1d', '#', '"']
if color == "red":
    c1,c2,c3,c4,c5 = ['\x15', '!', '\x1f', '#', '"']
if color == "white":
    c1,c2,c3,c4,c5 = ['$', '#', '#', '"', '"']
if color == "green":
    c1,c2,c3,c4,c5 = ['\x1a', '\x19', '\x19', '#', '"']
entitylist.append(["neon",(x,y,z),2,2,5,c1,c2,c3,c4,c5])
self.client.sendServerMessage("Neon has been created.")
