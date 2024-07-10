import os
import numpy as np

try:
    from xrayphysics import *
    has_physics = True
except:
    has_physics = False

def parsePDstring(text):
    retVal = None
    if len(text) > 0:
        string_objects = text.split('}')
        for n in range(len(string_objects)):
            string_object = string_objects[n]
            pdic = {}
            if len(string_object) > 0:
                string_object = string_object.replace('{','')
                string_object = string_object.replace('}','')
                string_object = string_object.strip()
                key_values = string_object.split(';')
                for m in range(len(key_values)):
                    if len(key_values[m].split('=')) == 2:
                        key = key_values[m].split('=')[0].strip()
                        value = key_values[m].split('=')[1].strip()
                        #print('key = ' + str(key) + ', value = ' + str(value))
                        pdic[key] = value
            if len(pdic) > 0:
                if retVal is None:
                    retVal = [pdic]
                else:
                    retVal.append(pdic)
    return retVal
    
def parseFilters(text):
    retVal = None
    if has_physics and len(text) > 0:
        all_filters = parsePDstring(text)
        for n in range(len(all_filters)):
            filter = all_filters[n]
            if 'thickness' in filter.keys():
                thickness = filter['thickness']
            else:
                print('Error: invalid filter string (does not include thickness)')
                return None
            if 'material' in filter.keys():
                material = filter['material']
                if retVal is None:
                    retVal = [(material, None, thickness)]
                else:
                    retVal.append((material, None, thickness))
            else:
                if 'formula' in filter.keys():
                    formula = filter['formula']
                else:
                    print('Error: invalid filter string (does not include material or formula)')
                    return None
                if 'rho' in filter.keys():
                    mass_density = filter['rho']
                elif 'rhoe' in filter.keys():
                    mass_density = physics.rho(formula, float(filter['rhoe']))
                else:
                    print('Error: invalid filter string (does not include density)')
                    return None
                    
                if retVal is None:
                    retVal = [(formula, mass_density, thickness)]
                else:
                    retVal.append((formula, mass_density, thickness))
                
    return retVal
    
def parseMaterials(text):
    retVal = None
    if has_physics and len(text) > 0:
        all_filters = parsePDstring(text)
        for n in range(len(all_filters)):
            filter = all_filters[n]
            if 'material' in filter.keys():
                material = filter['material']
                if retVal is None:
                    retVal = [(material, None)]
                else:
                    retVal.append((material, None))
            else:
                if 'formula' in filter.keys():
                    formula = filter['formula']
                else:
                    print('Error: invalid filter string (does not include material or formula)')
                    return None
                if 'rho' in filter.keys():
                    mass_density = filter['rho']
                elif 'rhoe' in filter.keys():
                    mass_density = physics.rho(formula, float(filter['rhoe']))
                else:
                    print('Error: invalid filter string (does not include density)')
                    return None
                    
                if retVal is None:
                    retVal = [(formula, mass_density)]
                else:
                    retVal.append((formula, mass_density))
                
    return retVal
    
    
#retVal = parsePDstring('{material=water}{formula=H2O; rho=1.2e-3}')
retVal = parseMaterials('{material=water}{formula=H2O; rho=1.2e-3}')
#retVal = parseFilters('{material=Al; thickness=2}{formula=Cu; rho=7e-3; thickness=1}')
print(retVal)
