import sympy as sp
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import ast
from .materials import alum, sections_data, wood_data, alum_sections

def post_analysis(length, material, shape, axial_load, Ke, braced_axis, df, wood_type):
    
    #Get material paramters
    Emin = wood_data.loc[material]["Emin"]
    Fc = wood_data.loc[material]["Fc"]
    Fb = wood_data.loc[material]["Fb"]
    Ix = sections_data.loc[shape]["I_x"]
    depth = sections_data.loc[shape]["d"]
    width = sections_data.loc[shape]["b"]
    thickness = "n/a"
    Sx = sections_data.loc[shape]["S_x"]
    A = sections_data.loc[shape]["area"]

    #Assign values to mod factors before adjusint
    E_factor = 1
    C_factor = 1
    bending_factor = 1

    #Find effective length
    le = Ke * length
    
    #Find slenderness ratio
    if (braced_axis == "yes"):
        slenderness = le / depth
    else:
        slenderness = le / width

    #Check slenderness ratio
    if (slenderness > 50):
        slenderness_check = "Failed"
    else:
        slenderness_check = "Passed"
    
    #Find Emin adjusted with mod factors
    Emin_factor = 1.
    for index, i in df.iterrows():
        Emin_factor = Emin_factor * df.loc[index, 'Emin'] 
    Emin_adj = Emin * E_factor

    #Find FcE
    FcE = 0.822 * Emin_adj / (le / depth)**2

    #Find Fc_star (reference compresseion design value parallel to grain, excluding Cp, psi
    for index, i in df.iterrows():
        C_factor = C_factor * df.loc[index, 'Fc'] 
    Fc_star = Fc * C_factor

    #Find c (dependent on wood type)
    if(wood_type == "Glulam"):
       c = 0.9
    else:
        c = 0.8
    
    #Find Cp (column stability factor)
    Cp = (1 + (FcE / Fc_star)) / (2 * c) - ((1 + (FcE / Fc_star) / (2 * c))**2 - (FcE / Fc_star / c))**0.5

    #Find F_c (compression strength)
    F_c = Fc_star * Cp

    #Find fc (axial demand)
    fc = axial_load / A

    #Axial check
    if (F_c >= fc):
        axial_check = "Passed"
    else:
        axial_check = "Failed"

    #Find adjusting bending moment capacity
    for index, i in df.iterrows():
        bending_factor = bending_factor * df.loc[index, 'Fb'] 
    F_b = bending_factor * Fb

    #Bending slenderness ratio
    Rb = (le * depth / width**2)**0.5

    #Find FbE
    FbE = 1.2 * Emin_adj / Rb**2

    #Find bending stress due to eccentricity (fb)
    e = 0.05 * 12   #Assumed eccentricity
    moment = e * length
    fb = Sx * moment

    #Bending check
    if (F_b >= fb):
        bending_check = "Passed"
    else:
        bending_check = "Failed"

    #Combined check
    if (((fc / F_c)**2 + (fb / (F_b * (fc / FcE)))) <= 1 and fc / FcE + (fb / FbE)**2 <= 1):
        comb_check = "Passed"
    else:
        comb_check = "Failed"

    #Export parameters
    parameters = {'Depth': depth, 'Width': width, 'Thickness': thickness, 'Ix': Ix, 'Sx': Sx, 'Emin': Emin, 'A': A}

    return(le, slenderness, slenderness_check, Emin_adj, FcE, Fc_star, c, Cp, F_c, fc, axial_check, e, moment, Rb, FbE, F_b, fb, bending_check, comb_check, parameters)

    
    

    


    
    