# The Nexus software is licensed under the BSD 2-Clause license.
#
# You should have recieved a copy of this license with the software.
# If you did not, you can find one at the following link.
#
# http://opensource.org/licenses/bsd-license.php


"""
Decorators for protocol (command) methods.
"""

def owner_only(func):
    "Decorator for owner-only command methods."
    func.owner_only = True
    return func

def director_only(func):
    "Decorator for director-only command methods."
    func.director_only = True
    return func

def coder_only(func):
    "Decorator for coder-only command methods."
    func.coder_only = True
    return func

def admin_only(func):
    "Decorator for admin-only command methods."
    func.admin_only = True
    return func

def mod_only(func):
    "Decorator for mod-only command methods."
    func.mod_only = True
    return func

def member_only(func):
    "Decorator for member-only command methods."
    func.member_only = True
    return func

def worldowner_only(func):
    "Decorator for worldowner-only command methods."
    func.worldowner_only = True
    return func

def op_only(func):
    "Decorator for op-only command methods."
    func.op_only = True
    return func

def builder_only(func):
    "Decorator for builder-only command methods."
    func.builder_only = True
    return func

def unsilenced_only(func):
    "Decorator for unsilenced-only command methods."
    func.unsilenced_only = True
    return func

def build_list(func):
    "Decorator for build-list category methods."
    func.build_list = True
    return func

def world_list(func):
    "Decorator for world-list category methods."
    func.world_list = True
    return func

def player_list(func):
    "Decorator for player-list category methods."
    func.player_list = True
    return func

def info_list(func):
    "Decorator for info-list category methods."
    func.info_list = True
    return func

def username_command(func):
    "Decorator for commands that accept a single username parameter, and need a Client"
    def inner(self, parts, fromloc, overriderank):
        if len(parts) == 1:
            self.client.sendServerMessage("Please specify a username.")
        else:
            user = self.client.msgfindUserPartial(parts[1])
            if user != None:
                if len(parts) > 2:
                    try:
                        func(self, user, fromloc, overriderank, parts[2:])
                    except:
                        self.client.sendServerMessage("You specificed too many arguments.")
                else:
                    func(self, user, fromloc, overriderank)
    inner.__doc__ = func.__doc__
    return inner

def only_string_command(string_name):
    def only_inner(func):
        "Decorator for commands that accept a single username/plugin/etc parameter, and don't need it checked"
        def inner(self, parts, fromloc, overriderank):
            if len(parts) == 1:
                self.client.sendServerMessage("Please specify a %s." % string_name)
            else:
                username = parts[1].lower()
                func(self, username, fromloc, overriderank)
        inner.__doc__ = func.__doc__
        return inner
    return only_inner

only_username_command = only_string_command("username")

def only_partialusername_command(func):
    "Decorator for commands that accept only a username, which can be just part of a full name"
    def inner(self, parts, fromloc, overriderank):
        if len(parts) == 1:
            self.client.sendServerMessage("Please specify a username.")
        else:
            name = parts[1].lower()
            # Try to match as a full name first.
            if name not in self.client.factory.usernames:
                # Build a list of any partial matches.
                matches = []
                for username in self.client.factory.usernames:
                    if name in username:
                        matches.append(username)
                if len(matches)==0:
                    self.client.sendServerMessage("No such user '%s' (3+ chars?)" % name)
                    return
                elif len(matches) > 1:
                    self.client.sendServerMessage("'%s' matches multiple users. Be more specific." % name)
                    return
                else:
                    name = matches[0]
            func(self, name, fromloc, overriderank)
    inner.__doc__ = func.__doc__
    return inner

def username_world_command(func):
    "Decorator for commands that accept a single username parameter and possibly a world name."
    def inner(self, parts, fromloc, overriderank):
        if len(parts) == 1:
            self.client.sendServerMessage("Please specify a username.")
        else:
            username = parts[1].lower()
            if len(parts) == 3:
                try:
                    world = self.client.factory.worlds[parts[2].lower()]
                except KeyError:
                    self.client.sendServerMessage("Unknown world '%s'." % parts[2].lower())
                    return
            else:
                world = self.client.world
            func(self, username, world, fromloc, overriderank)
    inner.__doc__ = func.__doc__
    return inner

def on_off_command(func):
    "Decorator for commands that accept a single on/off parameter"
    def inner(self, parts, fromloc, overriderank):
        if len(parts) == 1:
            self.client.sendServerMessage("Please use '%s on' or '%s off'." % (parts[0], parts[0]))
        else:
            if parts[1].lower() not in ["on", "off"]:
                self.client.sendServerMessage("Use 'on' or 'off', not '%s'" % parts[1])
            else:
                func(self, parts[1].lower(), fromloc, overriderank)
    inner.__doc__ = func.__doc__
    return inner
