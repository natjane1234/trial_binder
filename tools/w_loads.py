# The loads class takes dead, live.... loads as arguments, and uses methods to assign load cases to elements
# Loads can be put input as distibuted, psf, or point loads, depending on the method chosen
# This is the only module that defaults to psf, lb, and lb/ft (due to how loads are typically specified)
# All outputs will be in kips, in, and kip/in

import pandas as pd
class Loads():

    def __init__(self, supports = None, pt_loads = None, loads = None, supports_service = None, pt_loads_service = None, loads_service = None, supports_ll = None, pt_loads_ll = None, loads_ll = None):
        """
        Applies loads to beams and returns moment shear, and 
        service load deflections
        
        Parameters:
        supports (list of lists): list of lists of points relative to beam starting (in) (only simple supports) (forces will be added as second list item at end)
        pt_loads (list of lists): list of lists of points rel to beam start (in), and force (kips) (positive is downwards)
        loads (list of lists): list of lists of uniform loads with start (in), end (in), and load (kips/in) (positive is downwards)
        """

        self.supports = supports
        self.pt_loads = pt_loads
        self.loads = loads
        self.supports_service = supports_service
        self.pt_loads_service = pt_loads_service
        self.loads_service = loads_service
        self.supports_ll = supports_ll
        self.pt_loads_ll = pt_loads_ll
        self.loads_ll = loads_ll

# Below is the start of a bettter loads class, needs work
