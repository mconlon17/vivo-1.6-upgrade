
#
#  Test get_person
#
import vivotools as vt

print vt.get_person("http://vivo.ufl.edu/individual/n13049") # Richard Macmaster
print vt.get_person("http://vivo.ufl.edu/individual/n3698",get_positions=True) # Chelsea Dinsmore
print vt.get_person("http://vivo.ufl.edu/individual/n25562",get_positions=True) # Mike Conlon
print vt.get_person("http://vivo.ufl.edu/individual/n1770144435",get_positions=True) # Colleen Abad
