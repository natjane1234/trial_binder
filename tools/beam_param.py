
from .materials import alum, sections_data, wood_data, alum_sections
import pandas as pd
def beam_param(material, shape):
    """Return beam parameters"""

    if material == "Aluminum":
        E = alum["E"]
        Ix = alum_sections.loc[shape]["Ix"]
        depth = alum_sections.loc[shape]["depth"]
        width = alum_sections.loc[shape]["width"]
        thickness = alum_sections.loc[shape]["thickness"]
        Sx = alum_sections.loc[shape]["Sx"]
        A = alum_sections.loc[shape]["area"]
    else:
        E = wood_data.loc[material]["E"] / 1000
        Ix = sections_data.loc[shape]["I_x"]
        depth = sections_data.loc[shape]["d"]
        width = sections_data.loc[shape]["b"]
        thickness = "n/a"
        Sx = sections_data.loc[shape]["S_x"]
        A = sections_data.loc[shape]["area"]

    #Export parameters
    parameters = {
        "Parameter": ["Depth", "Width", "Thickness", "Ix", "Sx", "E", "A"],
        "Value": [round(depth,1), round(width,2), thickness, round(Ix,1), round(Sx,1), round(E,0), round(A,2)],
        "Unit": ["in", "in", "in", "in^4", "in^3", "ksi", "in^2"]
    }
    
    param_data = pd.DataFrame(parameters)
    param_data.set_index('Parameter', inplace = True)
    return(param_data)