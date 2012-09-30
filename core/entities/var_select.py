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

if len(parts) < 5:
    self.client.sendServerMessage("For Make-a-Mob please use:")
    self.client.sendServerMessage("/entity var blocktype MovementBehavior NearBehavior")
    self.client.sendServerMessage("MovementBehavior: follow engulf pet random none")
    self.client.sendServerMessage("NearBehavior: kill explode none")
    var_continue = False
else:
    if parts[2] == 0 or parts[2].lower() == "air" or parts[2].lower() == "blank" or parts[2].lower() == "clear" or parts[2].lower() == "empty" or parts[2].lower() == "none" or parts[2].lower() == "nothing":
        self.client.sendServerMessage("Sorry, no invisible Make-a-Mobs allowed.")
        var_continue = False
    if var_continue:
        try:
            block = int(parts[2])
        except ValueError:
            try:
                block = globals()['BLOCK_%s' % parts[2].upper()]
            except KeyError:
                self.client.sendServerMessage("'%s' is not a valid block type." % parts[2])
                var_continue = False
        if var_continue:
            validmovebehaviors = ["follow","engulf","pet","random","none"]
            movementbehavior = parts[3]
            if movementbehavior not in validmovebehaviors:
                self.client.sendServerMessage("'%s' is not a valid MovementBehavior." % movementbehavior)
                var_continue = False
            if var_continue:
                validnearbehaviors = ["kill","explode","none"]
                nearbehavior = parts[4]
                if nearbehavior not in validnearbehaviors:
                    self.client.sendServerMessage("'%s' is not a valid NearBehavior." % nearbehavior)
                    var_continue = False
                if var_continue:
                    self.var_entityselected = "var"
                    self.var_entityparts = [block,movementbehavior,nearbehavior]
