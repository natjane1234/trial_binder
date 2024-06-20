from cls_wood_beam import Beam

class WoodBeam(Beam):
    """This class represents a wood beam."""
    def __init__(self, name, shape, material, length, supports, service, loads, service_loads, live_loads, pt_loads, service_pt_loads, live_pt_loads, description, df):
        super().__init__(name, shape, material, length, supports, service, loads, service_loads, live_loads, pt_loads, service_pt_loads, live_pt_loads, description)
        self.df = self.df

    def capacity(self):
        """Return beam capacity with mod factors applied"""

        perp_comp_factor = 1.
        comp_factor = 1.
        shear_factor = 1.
        bending_factor = 1.
        E_factor = 1.

        for index, i in df.iterrows():
            comp_factor = perp_comp_factor * self.df.loc[index, 'Fc']
            perp_comp_factor = perp_comp_factor * self.df.loc[index, 'FcP'] 
            shear_factor = shear_factor * self.df.loc[index, 'Fv'] 
            bending_factor = bending_factor * self.df.loc[index, 'Fb'] 
            E_factor = E_factor * self.df.loc[index, 'E'] 

        self.comp_strength = Fc * comp_factor
        self.perp_comp_strength = Fcp * perp_comp_factor
        self.shear_strength = Fv * shear_factor
        self.bending_strength = Fb * bending_factor
        self.E_adj = E * E_factor
    
    def udl_loads(self, trib_load, trib_width, trib_dl, trib_ll):
        """Return results of beam check with udl loads & any support conditions"""
        self.loads = [(trib_load / 12 / 12) * trib_width / 1000]
        self.service_loads = [((trib_dl + trib_ll) /12 /12) * trib_width  / 1000]  #kips/in
        self.live_loads = [(trib_ll /12 /12) * trib_width  / 1000]  #kips/in

        # Calls beam_analysis from cls_wood_beam.py to find max M, V, etc...
        self.beam_total_analysis()

        self.bearing_area = self.V_max * 1000 / self.perp_comp_strength
        self.bearing_length = self.bearing_area /  self.param["Width"]

        if (abs(self.bending_stress) < self.bending_strength):
            self.bending_check = "Passed"
        else:
            self.bending_check = "Failed"
        if (abs(self.shear_stress) < self.shear_strength):
            self.shear_check = "Passed"
        else:
            self.shear_check = "Failed"
        if (self.length_input.value > abs(self.bearing_length) and self.param['A'] > abs(self.bearing_area)):
            self.bearing_check = "Passed"
        else:
            self.bearing_check = "Failed"

