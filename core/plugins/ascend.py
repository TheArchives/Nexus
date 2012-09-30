from core.constants import *
from core.decorators import *
from core.server import *
from core.protocol import *

class AscendDescendPlugin(ProtocolPlugin):

    commands = {
        "ascend": "commandAscend",
        "descend": "commandDescend",

        }

    @op_only
    def commandAscend(self, parts, fromloc, overriderank):
        "/ascend <height> - Admin\nAscend a given height."
        if len(parts) != 2:
            self.client.sendServerMessage("Please include a height and no more.")
        else:
            height = int(parts[1])
            x, y, z, h, p = self.client.x>>5, self.client.y>>5, self.client.z>>5, self.client.h, self.client.p
            self.client.teleportTo(x, (y + height), z, h, p)
            self.client.sendServerMessage("Ascended %s blocks." % parts[1])

    @op_only
    def commandDescend(self, parts, fromloc, overriderank):
        "/descend <height> - Admin\nDescend a given height."
        if len(parts) != 2:
            self.client.sendServerMessage("Please include a height and no more.")
        else:
            height = int(parts[1])
            x, y, z, h, p = self.client.x>>5, self.client.y>>5, self.client.z>>5, self.client.h, self.client.p
            self.client.teleportTo(x, (y - height), z, h, p)
            self.client.sendServerMessage("Descended %s blocks." % parts[1])
            
