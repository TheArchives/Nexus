# The Nexus software is licensed under the BSD 2-Clause license.
#
# You should have recieved a copy of this license with the software.
# If you did not, you can find one at the following link.
#
# http://opensource.org/licenses/bsd-license.php

import time


def Rank(self, parts, fromloc, overriderank, server=None):
    username = parts[2].lower()
    year = time.strftime("%Y")
    month = time.strftime("%m")
    if username == "099":
        if not (int(year) > 2012 and int(month) > 3):
            return "099 may not be ranked until April 1st 2013."
    if server:
        factory = server
    else:
        factory = self.client.factory
    if parts[1] == "builder":
        if len(parts) > 3:
            try:
                world = factory.worlds[parts[3]]
            except KeyError:
                return ("Unknown world \"%s\"" %parts[3])
        else:
            if not server:
                world = self.client.world
            else:
                return "You must provide a world"
        if not server:
            if not overriderank:
                if not (world.isOp(self.client.username) or world.isOwner(self.client.username) or self.client.isModPlus()):
                    return ("You are not a high enough rank!")
        else:
            if fromloc != "console":
                if not (world.isOp(parts[-1]) or world.isOwner(parts[-1]) or factory.isModPlus(parts[-1])):
                    return ("You are not a high enough rank!")
        world.builders.add(username)
        if username in factory.usernames:
            user = factory.usernames[username]
            if user.world == world:
                user.sendBuilderUpdate()
        return ("%s is now a Builder" % username)
    elif parts[1] == "op":
        if len(parts) > 3:
            try:
                world = factory.worlds[parts[3]]
            except KeyError:
                return ("Unknown world \"%s\"" %parts[3])
        else:
            if not server:
                world = self.client.world
            else:
                return "You must provide a world"
        if not server:
            if not overriderank:
                if not (world.isOwner(self.client.username) or self.client.isModPlus()):
                    return ("You are not a high enough rank!")
        else:
            if fromloc != "console":
                if not (world.isOwner(parts[-1]) or factory.isModPlus(parts[-1])):
                    return ("You are not a high enough rank!")
        world.ops.add(username)
        return ("Opped %s" % username)
    elif parts[1] == "worldowner":
        if len(parts) > 3:
            try:
                world = factory.worlds[parts[3]]
            except KeyError:
                return ("Unknown world \"%s\"" %parts[3])
        else:
            if not server:
                world = self.client.world
            else:
                return "You must provide a world"
        if not server:
            if not self.client.isWorldOwnerPlus() or overriderank:
                return ("You are not a high enough rank!")
        else:
            if fromloc != "console":
                if not (world.isOwner(parts[-1]) or factory.isModPlus(parts[-1])):
                    return ("You are not a high enough rank!")
        self.client.world.owner = (username)
        return ("%s is now a World Owner." % username)
    elif parts[1] == "member":
        if not server:
            if not self.client.isModPlus():
                return ("You are not a high enough rank!")
        else:
            if fromloc != "console":
                if not factory.isModPlus(parts[-1]):
                    return ("You are not a high enough rank!")
        factory.members.add(username)
        if username in factory.usernames:
            factory.usernames[username].sendMemberUpdate()
        return ("%s is now a Member." % username)
    elif parts[1] == "globalbuilder":
        if not server:
            if not self.client.isModPlus():
                return ("You are not a high enough rank!")
        else:
            if fromloc != "console":
                if not factory.isModPlus(parts[-1]):
                    return ("You are not a high enough rank!")
        factory.globalbuilders.add(username)
        if username in factory.usernames:
            factory.usernames[username].sendGlobalBuilderUpdate()
        return ("%s is now a Global Builder." % username)
    elif parts[1] == "mod":
        if not server:
            if not self.client.isDirectorPlus():
                return ("You are not a high enough rank!")
        else:
            if fromloc != "console":
                if not factory.isDirectorPlus(parts[-1]):
                    return ("You are not a high enough rank!")
        factory.mods.add(username)
        if username in factory.usernames:
            factory.usernames[username].sendModUpdate()
        return ("%s is now a Mod." % username)
    elif parts[1] == "admin":
        if not server:
            if not self.client.isDirectorPlus():
                return ("You are not a high enough rank!")
        else:
            if fromloc != "console":
                if not factory.isDirectorPlus(parts[-1]):
                    return ("You are not a high enough rank!")
        factory.admins.add(username)
        if username in factory.usernames:
            factory.usernames[username].sendAdminUpdate()
        return ("%s is now an admin." % username)
    elif parts[1] == "coder":
        if not server:
            if not self.client.isDirectorPlus():
                return ("You are not a high enough rank!")
        else:
            if fromloc != "console":
                if not factory.isDirectorPlus(parts[-1]):
                    return ("You are not a high enough rank!")
        factory.coders.add(username)
        if username in factory.usernames:
            factory.usernames[username].sendCoderUpdate()
        return ("%s is now a coder." % username)
    elif parts[1] == "director":
        if not server:
            if not self.client.isHiddenPlus():
                return ("You are not a high enough rank!")
        else:
            if fromloc != "console":
                if not factory.isHiddenPlus(parts[-1]):
                    return ("You are not a high enough rank!")
        factory.directors.add(username)
        if username in factory.usernames:
            factory.usernames[username].sendDirectorUpdate()
        return ("%s is now an director." % username)
    elif parts[1] == "hidden":
        if not server:
            if not self.client.isServerOwner():
                return ("You are not a high enough rank!")
        else:
            if fromloc != "console":
                if not factory.isServerOwner(parts[-1]):
                    return ("You are not a high enough rank!")
        factory.hidden.add(username)
        if username in factory.usernames:
            factory.usernames[username].sendHiddenUpdate()
        return ("%s is now hidden." % username)
    else:
        return ("Unknown rank \"%s\""%parts[1])

def DeRank(self, parts, fromloc, overriderank, server=None):
    username = parts[2].lower()
    if server:
        factory = server
    else:
        factory = self.client.factory
    if parts[1] == "builder":
        if len(parts) > 3:
            try:
                world = factory.worlds[parts[3]]
            except KeyError:
                return ("Unknown world \"%s\"" %parts[3])
        else:
            if not server:
                world = self.client.world
            else:
                return "You must provide a world"
        if not server:
            if not overriderank:
                if not (world.isOp(self.client.username) or world.isOwner(self.client.username) or self.client.isModPlus()):
                    return ("You are not a high enough rank!")
        else:
            if fromloc != "console":
                if not (world.isOp(parts[-1]) or world.isOwner(parts[-1]) or factory.isModPlus(parts[-1])):
                    return ("You are not a high enough rank!")
        try:
            world.builders.remove(username)
        except KeyError:
                return ("%s is not a Builder." % username)
        if username in factory.usernames:
            user = factory.usernames[username]
            if user.world == world:
                user.sendBuilderUpdate()
        return ("Removed %s as Builder" % username)
    elif parts[1] == "op":
        if len(parts) > 3:
            try:
                world = factory.worlds[parts[3]]
            except KeyError:
                return ("Unknown world \"%s\"" %parts[3])
        else:
            if not server:
                world = self.client.world
            else:
                return "You must provide a world"
        if not server:
            if not overriderank:
                if not (world.isOwner(self.client.username) or self.client.isModPlus()) and world != self.client.world:
                    return ("You are not a World Owner!")
        else:
            if fromloc != "console":
                if not (world.isOwner(parts[-1]) or factory.isModPlus(parts[-1])):
                    return ("You are not a high enough rank!")
        try:
            world.ops.remove(username)
        except KeyError:
            return ("%s is not an op." % username)
        if username in factory.usernames:
            user = factory.usernames[username]
            if user.world == world:
                user.sendOpUpdate()
        return ("Deopped %s" % username)
    elif parts[1] == "worldowner":
        if len(parts) > 3:
            try:
                world = factory.worlds[parts[3]]
            except KeyError:
                return ("Unknown world \"%s\"" %parts[3])
        else:
            if not server:
                world = self.client.world
            else:
                return "You must provide a world"
        if not server:
            if not (world.isOwner(self.client.username) or self.client.isModPlus()) and world != self.client.world:
                return ("You are not a World Owner!")
        else:
            if fromloc != "console":
                if not (world.isOwner(parts[-1]) or factory.isModPlus(parts[-1])):
                    return ("You are not a high enough rank!")
        try:
            self.client.world.owner = ("")
        except KeyError:
            return ("%s is not a world owner." % username)
        if username in factory.usernames:
            user = factory.usernames[username]
            if user.world == world:
                user.sendOpUpdate()
        return ("%s is no longer the World Owner." % username)
    elif parts[1] == "member":
        if not server:
            if not self.client.isModPlus():
                return ("You are not a high enough rank!")
        else:
            if fromloc != "console":
                if not factory.isModPlus(parts[-1]):
                    return ("You are not a high enough rank!")
        if username in factory.members:
            factory.members.remove(username)
        else:
            return ("No such member \"%s\"" % username.lower())
        if username in factory.usernames:
            factory.usernames[username].sendMemberUpdate()
        return ("%s is no longer a Member." % username.lower())
    elif parts[1] == "globalbuilder":
        if not server:
            if not self.client.isModPlus():
                return ("You are not a high enough rank!")
        else:
            if fromloc != "console":
                if not factory.isModPlus(parts[-1]):
                    return ("You are not a high enough rank!")
        if username in factory.globalbuilders:
            factory.globalbuilders.remove(username)
        else:
            return ("No such global builder \"%s\"" % username.lower())
        if username in factory.usernames:
            factory.usernames[username].sendGlobalBuilderUpdate()
        return ("%s is no longer a Member." % username.lower())
    elif parts[1] == "mod":
        if not server:
            if not self.client.isDirectorPlus():
                return ("You are not a high enough rank!")
        else:
            if fromloc != "console":
                if not factory.isDirectorPlus(parts[-1]):
                    return ("You are not a high enough rank!")
        if username in factory.mods:
            factory.mods.remove(username)
        else:
            return ("No such mod \"%s\"" % username.lower())
        if username in factory.usernames:
            factory.usernames[username].sendModUpdate()
        return ("%s is no longer a Mod." % username.lower())
    elif parts[1] == "admin":
        if not server:
            if not self.client.isDirectorPlus():
                return ("You are not a high enough rank!")
        else:
            if fromloc != "console":
                if not factory.isDirectorPlus(parts[-1]):
                    return ("You are not a high enough rank!")
        if username in factory.admins:
            factory.admins.remove(username)
            if username in factory.usernames:
                factory.usernames[username].sendAdminUpdate()
            return ("%s is no longer an admin." % username.lower())
        else:
            return ("No such admin \"%s\""% username.lower())
    elif parts[1] == "coder":
        if not server:
            if not self.client.isDirectorPlus():
                return ("You are not a high enough rank!")
        else:
            if fromloc != "console":
                if not factory.isDirectorPlus(parts[-1]):
                    return ("You are not a high enough rank!")
        if username in factory.coders:
            factory.coders.remove(username)
            if username in factory.usernames:
                factory.usernames[username].sendCoderUpdate()
            return ("%s is no longer a coder." % username.lower())
        else:
            return ("No such admin \"%s\""% username.lower())
    elif parts[1] == "director":
        if not server:
            if not self.client.isHiddenPlus():
                return ("You are not a high enough rank!")
        else:
            if fromloc != "console":
                if not factory.isHiddenPlus(parts[-1]):
                    return ("You are not a high enough rank!")
        if username in factory.directors:
            factory.directors.remove(username)
            if username in factory.usernames:
                factory.usernames[username].sendDirectorUpdate()
            return ("%s is no longer an director." % username.lower())
        else:
            return ("No such director \"%s\""% username.lower())
    elif parts[1] == "hidden":
        if not server:
            if not self.client.isServerOwner():
                return ("You are not a high enough rank!")
        else:
            if fromloc != "console":
                if not factory.isServerOwner(parts[-1]):
                    return ("You are not a high enough rank!")
        if username in factory.hidden:
            factory.hidden.remove(username)
            if username in factory.usernames:
                factory.usernames[username].sendHiddenUpdate()
            return ("%s is no longer hidden." % username.lower())
        else:
            return ("No such hidden \"%s\""% username.lower())
    else:
        return ("Unknown rank \"%s\""%parts[1])

def Spec(self, username, fromloc, overriderank, server=None):
    if server:
        factory = server
    else:
        factory = self.client.factory
    if username in factory.directors:
        return ("You cannot make staff a spec!")
    if username in factory.coders:
        return ("You cannot make staff a spec!")
    if username in factory.admins:
        return ("You cannot make staff a spec!")
    if username in factory.mods:
        return ("You cannot make staff a spec!")
    factory.spectators.add(username)
    if username in factory.usernames:
        factory.usernames[username].sendSpectatorUpdate()
    return ("%s is now a spec." % username)

def Staff(self, server=None):
    Temp = []
    if server:
        factory = server
    else:
        factory = self.client.factory
    if len(factory.directors):
        Temp.append (["Directors:"] + list(factory.directors))
    if len(factory.coders):
        Temp.append (["Coders:"] + list(factory.coders))
    if len(factory.admins):    
        Temp.append (["Admins:"] + list(factory.admins))
    if len(factory.mods):
        Temp.append (["Mods:"] + list(factory.mods))
    return Temp

def Credits(self=None):
    Temp = []
    Temp.append ("Thanks to the following people for making Arc possible...")
    Temp.append ("Mojang Specifications (Minecraft): Notch, dock, ez, ...")
    Temp.append ("Creator: aera (Myne and The Archives)")
    Temp.append ("Devs (Arc/The Archives): Adam01, gdude2002 (arbot), NotMeh, revenant,")
    Temp.append ("Devs (iCraft): AndrewPH, destroyerx1, Dwarfy, erronjason, eugo (Knossus), goober, gothfox, ntfwc, Saanix, sk8rjwd, tehcid, Varriount, willempiee")
    Temp.append ("Devs (blockBox): fizyplankton, tyteen4a03, UberFoX")
    Temp.append ("Others: 099, 2k10, Akai, Antoligy, Aquaskys, aythrea, Bidoof_King, Bioniclegenius (Red_Link), blahblahbal, BlueProtoman, CDRom, fragmer, GLaDOS (Cortana), iMak, Kelraider, MAup, MystX, PyroPyro, Rils, Roadcrosser, Roujo, setveen, TheUndeadFish, TkTech, Uninspired")
    return Temp

def makefile(filename):
    import os
    dir = os.path.dirname(filename)
    try:
        os.stat(dir)
    except:
        try:
            os.mkdir(dir)
        except OSError:
            pass
    if not os.path.exists(filename):
        with open(filename, "w") as f:
            f.write("")
    del os

def makedatfile(filename):
    import os
    dir = os.path.dirname(filename)
    try:
        os.stat(dir)
    except:
        try:
            os.mkdir(dir)
        except OSError:
            pass
    if not os.path.exists(filename):
        with open(filename, "w") as f:
            f.write("(dp1\n.")
    del os

def checkos(self):
    try:
        if (os.uname()[0] == "Darwin"):
            os = "Mac"
        else:
            os = "Linux"
    except:
        os = "Windows"
    return os
