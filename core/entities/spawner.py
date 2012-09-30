# The Nexus software is licensed under the BSD 2-Clause license.
#
# You should have recieved a copy of this license with the software.
# If you did not, you can find one at the following link.
#
# http://opensource.org/licenses/bsd-license.php


if len(entitylist) <= maxentitiesperworld:
    x,y,z = var_position
    randnum = randint(1,6)
    if randnum < 4:
        entitylist.append(["zombie",(x,y+1,z),8,8])
    elif randnum == 6:
        entitylist.append(["creeper",(x,y+1,z),8,8])
    else:
        entitylist.append(["blob",(x,y+1,z),8,8])
