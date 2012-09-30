# The Nexus software is licensed under the BSD 2-Clause license.
#
# You should have recieved a copy of this license with the software.
# If you did not, you can find one at the following link.
#
# http://opensource.org/licenses/bsd-license.php


if len(parts) < 3:
    self.client.sendServerMessage("Please give a color (blue, red, white, green)")
    var_continue = False
if var_continue:
    color = parts[2]
    if color not in ["blue","red","white","green"]:
        self.client.sendServerMessage("%s is not a valid color for neon." % color)
        var_continue = False
    if var_continue:
        self.var_entityparts = [color]
        self.var_entityselected = "neon"
