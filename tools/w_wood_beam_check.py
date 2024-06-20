# Creates class used to check woodBeam

from tools.w_wood_beam import woodBeam
from typing import Literal
from tools.w_loads import Loads
from tools.materials import sections_data, wood_data
from tools.beam_loads import beam_analysis

class woodBeamCheck(woodBeam, Loads):
    def __init__(self, material, shape, length, wet_service: Literal['Dry service', 'Wet service'] = 'EMC 19 or below', 
                temp: Literal['Normal', 'Elevated (100 degrees F < T <= 125 degrees F)', 'Elevated (above 125 degrees F)'] = 'Normal',
                stability: Literal['Laterally Supported', 'Discontinuous Lateral Support'] = 'Laterally Supported',
                flat_use: Literal['Strong Axis Bending', 'Weak Axis Bending'] = 'Strong Axis Bending',
                incising: Literal['Non-incised', 'Incised'] = 'Incised',
                repetitive: Literal['Non-repetitive', 'Repetitive'] = 'Non-repetitive',
                load_combo: Literal['1.2D + 1.6L(storage)', '1.2D + 1.6L', '1.4D', 'other'] = '1.2D + 1.6L',
                supports = None, pt_loads = [], loads = [], supports_service = None, pt_loads_service = [], loads_service = [], supports_ll = None, pt_loads_ll = [], loads_ll = []):
        
        woodBeam.__init__(self, material, shape, length, wet_service, temp, stability, flat_use, incising, repetitive, load_combo)
        Loads.__init__(self, supports, pt_loads, loads, supports_service, pt_loads_service, loads_service, supports_ll, pt_loads_ll, loads_ll)
        
        """ 
        Performs check of wood beam. As of now Loads is a placeholder class, but eventually will input D, L, etc.. and get the distributed loads from it
        To use this class, initiate with beam properties & loading (will automatically assign capacity to woodBeam object)
        Then call calc_loads & calc_service_loads to find max M, V, and deflection
        Then call calc_capacity_check to see if capacity is exceeded
        
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
        supports (list of lists): list of lists of points relative to beam starting (in) (only simple supports) (forces will be added as second list item at end)
        pt_loads (list of lists): list of lists of points rel to beam start (in), and force (kips) (positive is downwards)
        loads (list of lists): list of lists of uniform loads with start (in), end (in), and load (kips/in) (positive is downwards)
        
        Methods:
        calc_loads: Finds max M & V on beam
        calc_service_loads: Finds deflection on beam
        calc_capacity_check: Check capacity against max M, V, and deflection
        """
    def calc_loads(self):
        """
        Calculate the loads on the beam, by calling external function beam_analysis from beam_loads module
        Will change the values of self.M & self.V to new maximums
        Input factored load combos
        Input service loads to get deflection

        Parameters:
        supports (list of lists): list of lists of points relative to beam starting (in) (only simple supports) (forces will be added as second list item at end)
        pt_loads (list of lists): list of lists of points rel to beam start (in), and force (kips) (positive is downwards)
        loads (list of lists): list of lists of uniform loads with start (in), end (in), and load (kips/in) (positive is downwards)
        """

        self.M_array, self.V_array, self.defl_array, self.M, _, self.V, _, self.defl, self.supports, _ = beam_analysis (self.length, self.material, self.shape, self.supports, self.pt_loads, self.loads, show_plots=False) 

    def calc_service_defl(self, supports_service, pt_loads_service, loads_service, supports_ll, pt_loads_ll, loads_ll):
        """
        Calculate the service deflection
        
        Parameters:
        supports (list of lists): list of lists of points relative to beam starting (in) (only simple supports) (forces will be added as second list item at end)
        pt_loads (list of lists): list of lists of points rel to beam start (in), and force (kips) (positive is downwards)
        loads (list of lists): list of lists of uniform loads with start (in), end (in), and load (kips/in) (positive is downwards)
    
        """

        self.M_array_service, self.V_array_service, self.M_service, _, self.V_service, _, self.defl_service, self.supports_service, _ = beam_analysis (self.length, self.material, self.shape, supports_service, pt_loads_service, loads_service, show_plots=False)
        self.M_array_ll, self.V_array_ll, self.M_ll, _, self.V_ll, _, self.defl_ll, self.supports_ll, _ = beam_analysis (self.length, self.material, self.shape, supports_ll, pt_loads_ll, loads_ll, show_plots=False)

    def calc_capacity_check(self):
        """
        Calculate the beam capacity and maximum stress

        :return: dict, with beam capacity and maximum stresses ("Bending Stress", "Shear Stress", Bearing Area", "Bearing Length", "Bending Check", "Shear Check", "Bearing Check")
        """
        if self.capacity != "See NDS":
            bending_stress = self.M / sections_data.loc[self.shape,"S_x"]
            shear_stress = (3 / 2) * self.V / sections_data.loc[self.shape,"area"]
            bearing_area = self.V / self.capacity["Perp. Compression Strength"]
            bearing_length = bearing_area /  sections_data.loc[self.shape,"b"]

            if (abs(bending_stress) < self.capacity["Bending Strength"]):
                bending_check = "Passed"
            else:
                bending_check = "Failed"

            if abs(shear_stress) < self.capacity["Shear Strength"]:
                shear_check = "Passed"
            else:
                shear_check = "Failed"
            
            if hasattr(self, 'defl_service'):
                if abs(self.defl_service) < self.length / 240:
                    defl_service_check = "Passed"
                else:
                    defl_service_check = "Failed"
            else:
                defl_service_check = "No values given"

            if hasattr(self, 'defl_ll'):
                if abs(self.defl_ll) < self.length / 360:
                    defl_ll_check = "Passed"
                else:
                    defl_ll_check = "Failed"
            else:
                defl_ll_check = "No values given"

            self.capacity_check = {"Bending Stress": bending_stress, "Shear Stress": shear_stress, "Bearing Area": bearing_area, "Bearing Length": bearing_length, "Shear Check": shear_check, "Bending Check": bending_check, "Service Deflection Check": defl_service_check, "Live Load Deflection Check": defl_ll_check}
    
        else: 
            self.capacity_check = "See NDS"
