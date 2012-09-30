# The Nexus software is licensed under the BSD 2-Clause license.
#
# You should have recieved a copy of this license with the software.
# If you did not, you can find one at the following link.
#
# http://opensource.org/licenses/bsd-license.php


if block == 46:
    entitylist.append(["nuke",(x,y,z),1,1,True,24,5])
else:
    self.client.sendServerMessage("Please place TNT blocks.")
