# The Nexus software is licensed under the BSD 2-Clause license.
#
# You should have recieved a copy of this license with the software.
# If you did not, you can find one at the following link.
#
# http://opensource.org/licenses/bsd-license.php


proxintialdelay = entity[4]
if proxintialdelay <= 0:
    closestposition = (0,0)
    closestdistance = None
    for entry in userpositionlist:
        var_pos = entry[1]
        i,j,k = var_pos
        distance = ((i-x)**2+(j-y)**2+(k-z)**2)**0.5
        if closestdistance == None:
            closestdistance = distance
            closestposition = (var_pos[0],var_pos[2])
        else:
            if distance < closestdistance:
                closestdistance = distance
                closestposition = (var_pos[0],var_pos[2])
    if closestdistance < 3:
        entitylist.append(["tnt",(x,y,z),1,1,True,0,5])
        var_dellist.append(index)
else:
    proxintialdelay -= 1
    entity[4] = proxintialdelay
