# Performes capacity and load related calculations for a wood beam, based on AWC NDS 2024
# All parameters are in kips, in, and ksi
# Max moment and shear are input in kip-in and kips (they may be found from loading by calling an independent function beam_analysis) 
# Methods are named with prefix calc_ to differentiate them from return values
# All calculations LRFD

import math
from typing import Literal
import pandas as pd
import numpy as np
from enum import Enum
from tools.materials import sections_data, wood_data

class woodBeam:
    def __init__(self, material, shape, length, wet_service: Literal['Dry service', 'Wet service'] = 'Dry service', 
                temp: Literal['Normal', 'Elevated (100 degrees F < T <= 125 degrees F)', 'Elevated (above 125 degrees F)'] = 'Normal',
                stability: Literal['Laterally Supported', 'Discontinuous Lateral Support'] = 'Laterally Supported',
                flat_use: Literal['Strong Axis Bending', 'Weak Axis Bending'] = 'Strong Axis Bending',
                incising: Literal['Non-incised', 'Incised'] = 'Incised',
                repetitive: Literal['Non-repetitive', 'Repetitive'] = 'Non-repetitive',
                load_combo: Literal['1.2D + 1.6L(storage)', '1.2D + 1.6L', '1.4D', 'other'] = '1.2D + 1.6L'):
        """
        Initialize the woodBeam with the necessary factors. References are to NDS 2018.
        All values in kips or in
        All object parameters are calculated during intialization, but values are still passed to methods as parameters (calling object attributes
        with self. is avoided within methods where possible. Instead, self. attributes are passed to methods as parameters in object initialization).
        This allows methods can be called with different paramters to test different values.
        For example, objects will have an attirbute self.mod_factors with all of an initiated
        object's mod_factor, but the method calc_mod_factors can be called with any parameters to test
        new values, without changing the object's self.mod_factor attribute.
        All sawn lumber reference design values come from 2024 NDS Table 4A (Reference Design Values for Visually Graded Dimension Lumber (2"-4" thick))
        Note that LVL volume factor is an estimate based on ESRs, actual value should come from manufacturer

        Parameters:
        material (str): wood type, from list wood_data.index
        shape (str): wood shape, from list sections_data.index
        length (float): beam length (in)
        wet_service (str): wet service if sawn lumber MC > 19%, or LVL MC > 16%, NDS 4.1.4 & 8.3.3
        temp (str): temperature, NDS 2.3.3
        stability (str): lateral support, NDS 3.3.3
        flat_use (str): NDS 4.3.7
        incising (str): only applicable to sawn lumber, NDS 4.3.8
        repetitive (str): repetitive members must be spaced at max 24", have 3 or more memebters, and be joined by load distributing elements, NDS 4.3.9
        load_combo (str): effects time effec factor, see NDS N.3.3

        Methods:
        calc_mod_factors (static): called at instance initiation, returns mod_factors dataframe & assings to seld.mod_factors
        calc_capacity (static): called at instance initiation, returns capacity dictionary & assigns to self.capacity
        calc_capacity_check : can be called after instance initiation, with input values of M & V & defl, or after calc_loads & calc_service_loads is called, with new values of M & V & defl based on loads
        calc_loads: can be called to determine max M, V, and deflection on beam with different loading
        calc_service_loads: can be called to determine service load deflection on beam 
        """
        # Initiate all class input parameters as attributes
        self.material = material
        self.shape = shape
        self.temp = temp
        self.stability = stability
        self.flat_use = flat_use
        self.incising = incising
        self.repetitive = repetitive
        self.length = length
        self.wet_service = wet_service
        self.load_combo = load_combo
    
        # Call calc_mod_factors to find mod_factors (output as dataframe)
        self.mod_factors = self.calc_mod_factors(material = self.material, shape = self.shape, length = self.length, wet_service = self.wet_service, temp = self.temp, stability = self.stability, flat_use = self.flat_use, incising = self.incising, repetitive = self.repetitive, load_combo = self.load_combo)
        
        # Call calc_capacity to find capacity (output as dictionary)
        self.capacity = self.calc_capacity(material = self.material, mod_factors = self.mod_factors)

    
    @staticmethod
    def calc_mod_factors(material, shape, length, wet_service: Literal['Dry service', 'Wet service'] = 'EMC 19 or below', 
                temp: Literal['Normal', 'Elevated (100 degrees F < T <= 125 degrees F)', 'Elevated (above 125 degrees F)'] = 'Normal',
                stability: Literal['Laterally Supported', 'Discontinuous Lateral Support'] = 'Laterally Supported',
                flat_use: Literal['Strong Axis Bending', 'Weak Axis Bending'] = 'Strong Axis Bending',
                incising: Literal['Non-incised', 'Incised'] = 'Incised',
                repetitive: Literal['Non-repetitive', 'Repetitive'] = 'Non-repetitive',
                load_combo: Literal['1.2D + 1.6L(storage)', '1.2D + 1.6L', '1.4D', 'other'] = '1.2D + 1.6L'):
        """
        Finds wood mod factors based on NDS 2018 and input parameters
        if a mod factor does not apply, it is automatically set as 1.00 for the purposes of calculations
        
        Parameters:
        material (str): wood type
        shape (str): wood shape
        length (float): beam length
        wet_service (str): wet service if sawn lumber MC > 19%, or LVL MC > 16%, NDS 2018 4.1.4 & 5.1.4
        temp (str): temperature, NDS 2.3.3
        stability (str): lateral support, NDS 3.3.3
        flat_use (str): NDS 4.3.7, 5.3.7
        curvature (str): only applicable to LVL, NDS 5.3.8
        incising (str): only applicable to sawn lumber, NDS 4.3.8
        repetitive (str): sawn lumber only, repetitive members must be spaced at max 24", have 3 or more memebters, and be joined by load distributing elements, NDS 4.3.9
        load_combo (str): effects time effec factor, see NDS N.3.3

        :return: DataFrame, with all relevant mod factors on Fb, Fc, Fv, E, and Emin
        """
        # Define mod factors
        mod_factors = pd.DataFrame()
        #Mod factors for LVL
        if (material == "1.5E LVL" or material == "2.0E LVL" or material == "2.2E LVL"):
            
            # Create dataframe to hold mod factors for LVL
            mod_factors = pd.DataFrame(index=['Wet Service', 'Temperature', 'Beam Stability', 'Volume','Repetitive', 'Format', 'Resistance', 'Time Effect'],
                          columns=['Fb', 'Fv', 'Fc', 'FcP', 'E', 'Emin'])
            
            # Wet service factors, 8.3.3
            if wet_service == 'Wet service':
                mod_factors.loc["Wet Service", "Fb"] = "See NDS"
                mod_factors.loc["Wet Service", "Fv"]  = "See NDS"
                mod_factors.loc["Wet Service", "Fc"]  = "See NDS"
                mod_factors.loc["Wet Service", "FcP"]  = "See NDS"
                mod_factors.loc["Wet Service", "E"]  = "See NDS"
                mod_factors.loc["Wet Service", "Emin"]  = "See NDS"
        
            # Temperature factor (NDS Table 2.3.3)
            if temp == 'Elevated (100 degrees F < T <= 125 degrees F)':
                mod_factors.loc["Temperature", "Emin"]  = 0.9
                mod_factors.loc["Temperature", "E"]  = 0.9 
                if wet_service == 'Wet':
                    mod_factors.loc["Temperature", "Fb"] = 0.7
                    mod_factors.loc["Temperature", "Fv"]  = 0.7
                    mod_factors.loc["Temperature", "Fc"]  = 0.7
                    mod_factors.loc["Temperature", "FcP"]  = 0.7
                else:
                    mod_factors.loc["Temperature", "Fb"] = 0.8
                    mod_factors.loc["Temperature", "Fv"]  = 0.8
                    mod_factors.loc["Temperature", "Fc"]  = 0.8
                    mod_factors.loc["Temperature", "FcP"]  = 0.8
            elif temp == 'Elevated (above 125 degrees F)':
                mod_factors.loc["Temperature", "E"]  = 0.9
                mod_factors.loc["Temperature", "Emin"]  = 0.9
                if wet_service == 'Wet':
                    mod_factors.loc["Temperature", "Fb"] = 0.5
                    mod_factors.loc["Temperature", "Fv"]  = 0.5
                    mod_factors.loc["Temperature", "Fc"]  = 0.5
                    mod_factors.loc["Temperature", "FcP"]  = 0.5
                else:
                    mod_factors.loc["Temperature", "Fb"] = 0.7
                    mod_factors.loc["Temperature", "Fv"]  = 0.7
                    mod_factors.loc["Temperature", "Fc"]  = 0.7
                    mod_factors.loc["Temperature", "FcP"]  = 0.7
                
            # Stability factor
            if stability == 'Discontinuous Lateral Support':
                mod_factors.loc["Beam Stability", "Fb"] = "See NDS"
            else:
                mod_factors.loc["Beam Stability", "Fb"] = 1.00

            #Volume factor, 8.3.6. Should come from manufacturer. Estimate here is based on several ESRs.
            mod_factors.loc["Volume", "Fb"] = (12 / sections_data.loc[shape, "d"])**0.15

            # Repetitive factor
            if repetitive == 'Repetitive':
                mod_factors.loc["Repetitive", "Fb"] = 1.04
            
            # Column stability factor automatically calculated with column calcs
            # Bearing area factor excluded (conservative for Fcp)

        else:
            # Create dataframe to hold mod factors for sawn lumber (NDS 2024 Table 4A)
            mod_factors = pd.DataFrame(index=['Wet Service', 'Temperature', 'Beam Stability', 'Size', 'Flat Use', 'Incising', 'Repetitive', 'Format', 'Resistance', 'Time Effect'],
                        columns=['Fb', 'Fv', 'Fc', 'FcP', 'E', 'Emin'])

            # Wet service factors
            if wet_service == 'Wet service':
                mod_factors.loc["Wet Service", "Fb"] = 0.85
                mod_factors.loc["Wet Service", "Fv"]  = 0.97
                mod_factors.loc["Wet Service", "Fc"]  = 0.8
                mod_factors.loc["Wet Service", "FcP"]  = 0.67
                mod_factors.loc["Wet Service", "E"]  = 0.9
                mod_factors.loc["Wet Service", "Emin"]  = 0.9
        
            # Temperature factor (NDS Table 2.3.3)
            if temp == 'Elevated (100 degrees F < T <= 125 degrees F)':
                mod_factors.loc["Temperature", "Emin"]  = 0.9
                mod_factors.loc["Temperature", "E"]  = 0.9 
                if wet_service == 'Wet':
                    mod_factors.loc["Temperature", "Fb"] = 0.7
                    mod_factors.loc["Temperature", "Fv"]  = 0.7
                    mod_factors.loc["Temperature", "Fc"]  = 0.7
                    mod_factors.loc["Temperature", "FcP"]  = 0.7
                else:
                    mod_factors.loc["Temperature", "Fb"] = 0.8
                    mod_factors.loc["Temperature", "Fv"]  = 0.8
                    mod_factors.loc["Temperature", "Fc"]  = 0.8
                    mod_factors.loc["Temperature", "FcP"]  = 0.8
            elif temp == 'Elevated (above 125 degrees F)':
                mod_factors.loc["Temperature", "E"]  = 0.9
                mod_factors.loc["Temperature", "Emin"]  = 0.9
                if wet_service == 'Wet':
                    mod_factors.loc["Temperature", "Fb"] = 0.5
                    mod_factors.loc["Temperature", "Fv"]  = 0.5
                    mod_factors.loc["Temperature", "Fc"]  = 0.5
                    mod_factors.loc["Temperature", "FcP"]  = 0.5
                else:
                    mod_factors.loc["Temperature", "Fb"] = 0.7
                    mod_factors.loc["Temperature", "Fv"]  = 0.7
                    mod_factors.loc["Temperature", "Fc"]  = 0.7
                    mod_factors.loc["Temperature", "FcP"]  = 0.7
                
            # Stability factor (NDS 3.3.3)
            if stability == 'Laterally Supported' or sections_data.loc[shape, "d"] <= sections_data.loc[shape, "b"]:
                mod_factors.loc["Beam Stability", "Fb"] = 1.00
            else:
                mod_factors.loc["Beam Stability", "Fb"] = "See NDS"
        
            # Size factor based on Table 4A]
            if wood_data.loc[material, "Type"] == "Select Structural" or wood_data.loc[material, "Type"] == "No.1 & Btr" or wood_data.loc[material, "Type"] == "No.1" or wood_data.loc[material, "Type"] == "No.2" or wood_data.loc[material, "Type"] == "No.3":
                if sections_data.loc[shape, "d_nom"] == 2 or sections_data.loc[shape, "d_nom"] == 3 or sections_data.loc[shape, "d_nom"] == 4:
                    mod_factors.loc["Size", "Fb"] = 1.5
                    mod_factors.loc["Size", "Fc"] = 1.15
                elif sections_data.loc[shape, "d_nom"] == 5:
                    mod_factors.loc["Size", "Fb"] = 1.4
                    mod_factors.loc["Size", "Fc"] = 1.1
                elif sections_data.loc[shape, "d_nom"] == 6:
                    mod_factors.loc["Size", "Fb"] = 1.3
                    mod_factors.loc["Size", "Fc"] = 1.1
                elif sections_data.loc[shape, "d_nom"] == 8:
                    mod_factors.loc["Size", "Fc"] = 1.05
                    if sections_data.loc[shape, "b_nom"] == 4:
                        mod_factors.loc["Size", "Fb"] = 1.3
                    else:
                        mod_factors.loc["Size", "Fb"] = 1.2
                elif sections_data.loc[shape, "d_nom"] == 10:
                    mod_factors.loc["Size", "Fc"] = 1.0
                    if sections_data.loc[shape, "b_nom"] == 4:
                        mod_factors.loc["Size", "Fb"] = 1.2
                    else:
                        mod_factors.loc["Size", "Fb"] = 1.1
                elif sections_data.loc[shape, "d_nom"] == 12:
                    mod_factors.loc["Size", "Fc"] = 1.0
                    if sections_data.loc[shape, "b_nom"] == 4:
                        mod_factors.loc["Size", "Fb"] = 1.1
                    else:
                        mod_factors.loc["Size", "Fb"] = 1.0
                elif sections_data.loc[shape, "d_nom"] == 14:
                    mod_factors.loc["Size", "Fc"] = 0.9
                    if sections_data.loc[shape, "b_nom"] == 4:
                        mod_factors.loc["Size", "Fb"] = 1.0
                    else:
                        mod_factors.loc["Size", "Fb"] = 0.9

            elif wood_data.loc[material, "Type"] == "Stud":
                if sections_data.loc[shape, "d_nom"] == 2 or sections_data.loc[shape, "d_nom"] == 3 or sections_data.loc[shape, "d_nom"] == 4:
                    mod_factors.loc["Size", "Fb"] = 1.1
                    mod_factors.loc["Size", "Fc"] = 1.05
                elif sections_data.loc[shape, "d_nom"] == 5 or sections_data.loc[shape, "d_nom"] == 6:
                    mod_factors.loc["Size", "Fb"] = 1.0
                    mod_factors.loc["Size", "Fc"] = 1.0
                else:
                    mod_factors.loc["Size", "Fb"] = "See NDS"
                    mod_factors.loc["Size", "Fc"] = "See NDS"
            
            elif wood_data.loc[material, "Type"] == "Construction" or wood_data.loc[material, "Type"] == "Standard":
                mod_factors.loc["Size", "Fb"] = 1.0
                mod_factors.loc["Size", "Fc"] = 1.0
            elif wood_data.loc[material, "Type"] == "Utility":
                if sections_data.loc[shape, "d_nom"] == 4:
                    mod_factors.loc["Size", "Fb"] = 1.0
                    mod_factors.loc["Size", "Fc"] = 1.0
                else:
                    mod_factors.loc["Size", "Fb"] = 0.4
                    mod_factors.loc["Size", "Fc"] = 0.6   
        
            # Flat_use factor
            if flat_use == 'Weak axis bending':
                mod_factors.loc["Flat Use", "Fb"] = "See NDS"
        
            # Incising factor
            if incising == 'Incised':
                mod_factors.loc["Incising", "Fb"] = 0.8
                mod_factors.loc["Incising", "Fv"]  = 0.8
                mod_factors.loc["Incising", "Fc"]  = 0.8
                mod_factors.loc["Incising", "FcP"]  = 1.00
                mod_factors.loc["Incising", "E"]  = 0.95
                mod_factors.loc["Incising", "Emin"]  = 0.95

            # Repetitive factor
            if repetitive == 'Repetitive':
                mod_factors.loc["Repetitive", 'Fb'] = 1.15

            # Column stability factor automatically calculated with column calcs
            # Buckling stiffness factor excluded (conservative for Emin)
            # Buckling area factor excluded (conservative for Fcp)
        
        # Conversion factors for LVL and sawn lumber
        
        # Format conversion factor
        mod_factors.loc["Format", "Fb"] = 2.54
        mod_factors.loc["Format", "Fv"]  = 2.88
        mod_factors.loc["Format", "Fc"]  = 2.4
        mod_factors.loc["Format", "FcP"]  = 1.67
        mod_factors.loc["Format", "E"]  = 1.
        mod_factors.loc["Format", "Emin"]  = 1.76 

        # Resistance conversion factor
        mod_factors.loc["Resistance", "Fb"] = 0.85
        mod_factors.loc["Resistance", "Fv"]  = 0.75
        mod_factors.loc["Resistance", "Fc"]  = 0.9
        mod_factors.loc["Resistance", "FcP"]  = 0.9
        mod_factors.loc["Resistance", "E"]  = 1.
        mod_factors.loc["Resistance", "Emin"]  = 0.85 

        # Time effect factor, NDS Appendix N.3.3. If not one of the below load combos, time effect factor = 1
        if load_combo == "1.2D + 1.6L":
            mod_factors.loc["Time Effect", "Fb"] = 0.8
            mod_factors.loc["Time Effect", "Fv"]  = 0.8
            mod_factors.loc["Time Effect", "Fc"]  = 0.8
            mod_factors.loc["Time Effect", "FcP"]  = 1.
            mod_factors.loc["Time Effect", "E"]  = 1.
            mod_factors.loc["Time Effect", "Emin"]  = 1. 
        elif load_combo == "1.4D":
            mod_factors.loc["Time Effect", "Fb"] = 0.6
            mod_factors.loc["Time Effect", "Fv"]  = 0.6
            mod_factors.loc["Time Effect", "Fc"]  = 0.6
            mod_factors.loc["Time Effect", "FcP"]  = 1.
            mod_factors.loc["Time Effect", "E"]  = 1.
            mod_factors.loc["Time Effect", "Emin"]  = 1.
        elif load_combo == "1.2D + 1.6L(storage)":
            mod_factors.loc["Time Effect", "Fb"] = 0.7
            mod_factors.loc["Time Effect", "Fv"]  = 0.7
            mod_factors.loc["Time Effect", "Fc"]  = 0.7
            mod_factors.loc["Time Effect", "FcP"]  = 1.
            mod_factors.loc["Time Effect", "E"]  = 1.
            mod_factors.loc["Time Effect", "Emin"]  = 1. 

        # Fill all empty mod factors with 1
        mod_factors = mod_factors.fillna(1.)

        return mod_factors

    @staticmethod
    def calc_capacity(material, mod_factors):
        """
        Calculate the shear, bending and bearing strengths of the wood beam

        Parameters:
        material (str): Material of the beam
        shape (str): Shape of the beam
        mod_factors (pandas.DataFrame): DataFrame with the modified factors for the beam

        :return: dict, capacities of member with mod factor
        """
        
        perp_comp_factor = 1.
        comp_factor = 1.
        shear_factor = 1.
        bending_factor = 1.
        E_factor = 1.
        
        # Check that all values are floats (ie none are "See NDS")
        all_floats = mod_factors.select_dtypes(include=[float]).shape[1] == mod_factors.shape[1]
        
        if all_floats == True:
            for index, i in mod_factors.iterrows():
                comp_factor = perp_comp_factor * mod_factors.loc[index, 'Fc']
                perp_comp_factor = perp_comp_factor * mod_factors.loc[index, 'FcP'] 
                shear_factor = shear_factor * mod_factors.loc[index, 'Fv'] 
                bending_factor = bending_factor * mod_factors.loc[index, 'Fb'] 
                E_factor = E_factor * mod_factors.loc[index, 'E'] 
        
            #Strengths are in ksi
            comp_strength = wood_data.loc[material,"Fc"] * comp_factor / 1000
            perp_comp_strength = wood_data.loc[material,"FcP"] * perp_comp_factor / 1000
            shear_strength = wood_data.loc[material,"Fv"] * shear_factor / 1000
            bending_strength = wood_data.loc[material,"Fb"] * bending_factor / 1000
            E_adj = wood_data.loc[material,"E"]* E_factor / 1000

            capacity = {"Compression Strength": comp_strength, "Perp. Compression Strength": perp_comp_strength, "Shear Strength": shear_strength, "Bending Strength": bending_strength, "E_adj": E_adj}
            return capacity

        else:
            capacity = "See NDS"
            return capacity

   