
#!/usr/bin/python

import os, sys, shutil
import cPickle
from ConfigParser import RawConfigParser as ConfigParser


worldowners = {}

worldlist = os.listdir("worlds/")
print "Building world-owner index of %s worlds..." % len(worldlist)
for world in worldlist:
    if not world.startswith("."):
        config = ConfigParser()
        config.read('worlds/%s/world.meta' % world)
        owner = "n/a"
        if config.has_section("owner"):
            owner = config.get("owner", "owner").lower()
            if len(owner) == 0:
                owner = "n/a"
        if not owner in worldowners:
            worldowners[owner] = [world]
        else:
            worldowners[owner].append(world)
    
fp = open("config/data/worldowners.dat", "w")
cPickle.dump(worldowners, fp)
fp.close()

print "Done"
