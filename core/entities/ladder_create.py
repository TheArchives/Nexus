# The Nexus software is licensed under the BSD 2-Clause license.
#
# You should have recieved a copy of this license with the software.
# If you did not, you can find one at the following link.
#
# http://opensource.org/licenses/bsd-license.php


w = y
entitylist.append(["ladder",(x,y,z),7,7,w])
self.client.sendServerMessage("A ladder was created.")
self.client.sendSplitServerMessage("A single ladder teleports a person to the closest air block in its column.")
