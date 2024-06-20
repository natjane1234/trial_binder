from .cls_beam import Beam
from .materials import alum, sections_data, wood_data, alum_sections

class WoodBeam(Beam):
    """This class represents a wood beam."""
    def __init__(self, name = None, shape = None, material = None, length = None, supports = None, loads = None , service_loads = None, live_loads = None, pt_loads = None, service_pt_loads = None, live_pt_loads = None, dead_pt_loads = None, dead_loads = None, description = None):
        super().__init__(name=name, shape=shape, material=material, length=length, supports=supports, loads=loads, service_loads=service_loads, dead_loads = dead_loads, live_loads=live_loads, pt_loads=pt_loads, dead_pt_loads = dead_pt_loads, service_pt_loads=service_pt_loads, live_pt_loads=live_pt_loads, description=description)


    def capacity(self):
        """Return beam capacity with mod factors applied"""
        E = wood_data.loc[self.material]["E"] / 1000
        Fb = wood_data.loc[self.material,"Fb"]
        Ft = wood_data.loc[self.material,"Ft"]
        Fv = wood_data.loc[self.material,"Fv"]
        Fc = wood_data.loc[self.material,"Fc"]
        Fcp = wood_data.loc[self.material,"FcP"]
        Ix = sections_data.loc[self.shape]["I_x"]
        depth = sections_data.loc[self.shape]["d"]
        width = sections_data.loc[self.shape]["b"]
        thickness = "n/a"
        Sx = sections_data.loc[self.shape]["S_x"]
        A = sections_data.loc[self.shape]["area"]

        self.param = {"Depth": depth, "Width": width, "Thickness": thickness, "Ix": Ix, "Sx": Sx, "E": E, "A": A, "Fb": Fb, "Ft": Ft, "Fv": Fv, "Fc": Fc, "FcP": Fcp}

        perp_comp_factor = 1.
        comp_factor = 1.
        shear_factor = 1.
        bending_factor = 1.
        E_factor = 1.

        
        for index, i in self.df.iterrows():
            comp_factor = perp_comp_factor * self.df.loc[index, 'Fc']
            perp_comp_factor = perp_comp_factor * self.df.loc[index, 'FcP'] 
            shear_factor = shear_factor * self.df.loc[index, 'Fv'] 
            bending_factor = bending_factor * self.df.loc[index, 'Fb'] 
            E_factor = E_factor * self.df.loc[index, 'E'] 

        #Strengths are in ksi
        self.comp_strength = self.param["Fc"] * comp_factor / 1000
        self.perp_comp_strength = self.param["FcP"] * perp_comp_factor / 1000
        self.shear_strength = self.param["Fv"] * shear_factor / 1000
        self.bending_strength = self.param["Fb"] * bending_factor / 1000
        self.E_adj = self.param["E"]* E_factor / 1000
    
    def udl_loads(self, trib_load, trib_width, trib_dl, trib_ll):
        """Return results of beam check with udl loads & any support conditions"""

        #Put loads into format of lists with start, end, and kips/inch
        self.loads = [[0, self.length, (trib_load / 12 / 12) * trib_width / 1000]]
        self.service_loads = [[0, self.length,((trib_dl + trib_ll) /12 /12) * trib_width  / 1000]]  #kips/in
        self.live_loads = [[0, self.length,(trib_ll /12 /12) * trib_width  / 1000]]  #kips/in
        self.pt_loads = []
        self.service_pt_loads = []
        self.live_pt_loads = []

        # Calls beam_analysis from cls_wood_beam.py to find max M, V, etc...
        self.beam_total_analysis()
        self.capacity()

        self.bearing_area = self.V_max / self.perp_comp_strength
        self.bearing_length = self.bearing_area /  self.param["Width"]

        if (abs(self.bending_stress) < self.bending_strength):
            self.bending_check = "Passed"
        else:
            self.bending_check = "Failed"
        if (abs(self.shear_stress) < self.shear_strength):
            self.shear_check = "Passed"
        else:
            self.shear_check = "Failed"
        if (self.length > abs(self.bearing_length) and self.param['A'] > abs(self.bearing_area)):
            self.bearing_check = "Passed"
        else:
            self.bearing_check = "Failed"
        
        self.service_defl_all = self.length / 180
        self.live_defl_all = self.length / 240

        if(abs(self.service_defl_max) < self.service_defl_all):
            self.service_defl_check = "Passed"
        else:
            self.service_defl_check = "Failed"
        
        if((abs(self.live_defl_max) < self.live_defl_all)):
            self.live_defl_check = "Passed"
        else:
            self.live_defl_check = "Failed"

    def all_loads(self):
        """Return results of beam check with any loads & any support conditions"""

        # Calls beam_analysis from cls_wood_beam.py to find max M, V, etc...
        self.beam_total_analysis()
        self.capacity()

        self.bearing_area = self.V_max / self.perp_comp_strength
        self.bearing_length = self.bearing_area /  self.param["Width"]

        if (abs(self.bending_stress) < self.bending_strength):
            self.bending_check = "Passed"
        else:
            self.bending_check = "Failed"
        if (abs(self.shear_stress) < self.shear_strength):
            self.shear_check = "Passed"
        else:
            self.shear_check = "Failed"
        if (self.length > abs(self.bearing_length) and self.param['A'] > abs(self.bearing_area)):
            self.bearing_check = "Passed"
        else:
            self.bearing_check = "Failed"
        
        self.service_defl_all = self.length / 180
        self.live_defl_all = self.length / 240

        if(abs(self.service_defl_max) < self.service_defl_all):
            self.service_defl_check = "Passed"
        else:
            self.service_defl_check = "Failed"
        
        if((abs(self.live_defl_max) < self.live_defl_all)):
            self.live_defl_check = "Passed"
        else:
            self.live_defl_check = "Failed"
            
