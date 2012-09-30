#    iCraft is Copyright 2010-2011 both
#
#    The Archives team:
#                   <Adam Guy> adam@adam-guy.com AKA "Adam01"
#                   <Andrew Godwin> andrew@aeracode.org AKA "Aera"
#                   <Dylan Lukes> lukes.dylan@gmail.com AKA "revenant"
#                   <Gareth Coles> colesgareth2@hotmail.com AKA "gdude2002"
#
#    And,
#
#    The iCraft team:
#                   <Andrew Caluzzi> tehcid@gmail.com AKA "tehcid"
#                   <Andrew Dolgov> fox@bah.org.ru AKA "gothfox"
#                   <Andrew Horn> Andrew@GJOCommunity.com AKA "AndrewPH"
#                   <Brad Reardon> brad@bradness.co.cc AKA "PixelEater"
#                   <Clay Sweetser> CDBKJmom@aol.com AKA "Varriount"
#                   <James Kirslis> james@helplarge.com AKA "iKJames"
#                   <Jason Sayre> admin@erronjason.com AKA "erronjason"
#                   <Jonathon Dunford> sk8rjwd@yahoo.com AKA "sk8rjwd"
#                   <Joseph Connor> destroyerx100@gmail.com AKA "destroyerx1"
#                   <Kamyla Silva> supdawgyo@hotmail.com AKA "NotMeh"
#                   <Kristjan Gunnarsson> kristjang@ffsn.is AKA "eugo"
#                   <Nathan Coulombe> NathanCoulombe@hotmail.com AKA "Saanix"
#                   <Nick Tolrud> ntolrud@yahoo.com AKA "ntfwc"
#                   <Noel Benzinger> ronnygmod@gmail.com AKA "Dwarfy"
#                   <Randy Lyne> qcksilverdragon@gmail.com AKA "goober"
#                   <Willem van der Ploeg> willempieeploeg@live.nl AKA "willempiee"
#
#    Disclaimer: Parts of this code may have been contributed by the end-users.
#
#    iCraft is licensed under the Creative Commons
#    Attribution-NonCommercial-ShareAlike 3.0 Unported License.
#    To view a copy of this license, visit http://creativecommons.org/licenses/by-nc-sa/3.0/
#    Or, send a letter to Creative Commons, 171 2nd Street,
#    Suite 300, San Francisco, California, 94105, USA.

#!/usr/bin/python

import os, sys, datetime, logging, shutil
from reqs.twisted.internet import reactor
from reqs.twisted.internet.error import CannotListenError
from logging.handlers import SMTPHandler
from core.constants import *
from core.globals import *
from core.server import CoreFactory
from core.controller import ControllerFactory
from ConfigParser import RawConfigParser as ConfigParser

makefile("logs/")
makefile("logs/console/")
makefile("logs/console/console.log")

logging.basicConfig(
	format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
	level=("--debug" in sys.argv) and logging.DEBUG or logging.INFO,
	datefmt="%m/%d/%Y %H:%M:%S",
)

rotate = logging.handlers.TimedRotatingFileHandler(
	filename="logs/console/console.log", when="H",
	interval=6, backupCount=14,
)
rotate.setFormatter( logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s", "%m/%d/%Y %H:%M:%S") )
logging.root.addHandler(rotate)

logger = logging.getLogger("iCraft")
logger.info("Now starting up iCraft+ 1G version %s..." % VERSION)

makefile("core/archives/")
makefile("logs/chat.log")
makefile("logs/server.log")
makefile("logs/staff.log")
makefile("logs/whisper.log")
makefile("logs/world.log")
makefile("config/data/")
makedatfile("config/data/balances.dat")
makedatfile("config/data/inbox.dat")
makedatfile("config/data/jail.dat")
makedatfile("config/data/titles.dat")

factory = CoreFactory()
try:
    reactor.listenTCP(factory.config.getint("network", "port"), factory)
    reactor.listenTCP(30000, factory)
except CannotListenError:
    logger.critical("Something is already running on port %s" % (factory.config.getint("network", "port")))
    sys.exit(1)
controller = ControllerFactory(factory)
try:
    reactor.listenTCP(factory.config.getint("network", "controller_port"), controller)
except CannotListenError:
    logger.warning("Controller cannot listen on port %s. Disabled." % factory.config.getint("network", "port"))
    del controller

money_logger = logging.getLogger('TransactionLogger')
fh = logging.FileHandler('logs/server.log')
formatter = logging.Formatter("%(asctime)s: %(message)s")
fh.setFormatter(formatter)
money_logger.addHandler(fh)
try:
    reactor.run()
finally:
    logger.info("Saving server metas...")
    factory.saveMeta()
    logger.info("Flushing worlds to disk...")
    for world in factory.worlds.values():
        logger.info("Saving: %s" % world.basename)
        world.stop()
        world.save_meta()
    logger.info("Done flushing...")
    sys.exit(1)
