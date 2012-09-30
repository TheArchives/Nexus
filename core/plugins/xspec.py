import logging
from core.plugins import ProtocolPlugin
from core.decorators import *
from core.constants import *
from core.globals import *
from core.server import *
from reqs.twisted.internet import reactor
# maxundos = 3000

class xspec(ProtocolPlugin):
    commands = {
        "xspec": "commandXSpec",
        "uspec": "commandUSpec",
        }
    
    @mod_only
    @only_partialusername_command
    def commandXSpec(self, username, fromloc, overriderank):
        "/xspec username - Mod\nUndoes all builds by the user, specs them, and then kicks them."
        # /undo all <username>
        func = self.client.getCommandFunc("undo")
        if func is not None:
            func(("/undo", "all", username), "user", False)
        else:
            self.client.sendServerMessage("Error: Could not find Undo command.")
        # /spec <username>
        func = self.client.getCommandFunc("spec")
        if func is not None:
            func(("/spec", username), "user", False)
        else:
            self.client.sendServerMessage("Error: Could not find Spec command.")
        # /kick <username>
        func = self.client.getCommandFunc("kick")
        if func is not None:
            func(("/kick", username), "user", False)
        else:
            self.client.sendServerMessage("Error: Could not find Undo command.")
    
    @mod_only
    @only_partialusername_command
    def commandUSpec(self, username, fromloc, overriderank):
        "/uspec username - Mod\nUndoes all builds by the user and specs them."
        # /undo all <username>
        func = self.client.getCommandFunc("undo")
        if func is not None:
            func(("/undo", "all", username), "user", False)
        else:
            self.client.sendServerMessage("Error: Could not find Undo command.")
        # /spec <username>
        func = self.client.getCommandFunc("spec")
        if func is not None:
            func(("/spec", username), "user", False)
        else:
            self.client.sendServerMessage("Error: Could not find Spec command.")
