import sympy as sp
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import ast
from .materials import alum, sections_data, wood_data, alum_sections
import copy


class Loads:
    """Assigns parameters to different load objects."""
   
    def __init__(self, start, end, load):
        self.start = start
        self.end = end
        self.load = load

class Beam:
    """This class represents a beam (can be any material or shape)."""
    #Everything in this class is is in kips or inches
    #Several attributes that will not be assigned immediately are intiilized as None (if included as paramter in innit method the value can optionaly be set on object initialization)
    def __init__(self, name = None, shape = None, material = None, length = None, supports = None, loads = None , service_loads = None, live_loads = None, pt_loads = None, service_pt_loads = None, live_pt_loads = None, dead_pt_loads = None, dead_loads = None, description = None):
        self.name = name
        self.shape = shape
        self.material = material
        self.length = length
        self.supports = supports
        self.loads = loads
        self.service_loads = service_loads
        self.dead_loads = dead_loads
        self.live_loads = live_loads
        self.pt_loads = pt_loads
        self.service_pt_loads = service_pt_loads
        self.dead_pt_loads = dead_pt_loads
        self.live_pt_loads = live_pt_loads
        self.description = description
        self.relative_path = None
        self.absolute_path = None
        self.url = None
        self.output = None
        self.output_html = None

        #Beam is automatically assigned a dictionary with it's parameters
        if self.material == "Aluminum":
            E = alum["E"]
            Fb = alum["Fb"]
            Ft = alum["Ft"]
            Fv = alum["Fv"]
            Fc = alum["Fc"]
            Fcp = alum["FcP"]
            Ix = alum_sections.loc[self.shape]["Ix"]
            depth = alum_sections.loc[self.shape]["depth"]
            width = alum_sections.loc[self.shape]["width"]
            thickness = alum_sections.loc[self.shape]["thickness"]
            Sx = alum_sections.loc[self.shape]["Sx"]
            A = alum_sections.loc[self.shape]["area"]

    def beam_partial_analysis (self): 
        """Uses beam_analysis to find max moment, shear and deflection for one set of loads"""
        #Find max moment and shear using total loads, print moment and shear graphs
        self.M_vert, self.V_vert, self.defl_vert, self.M_max, self.bending_stress, self.V_max, self.shear_stress, self.defl_max, self.supports = self.beam_analysis(self.loads, self.pt_loads, self.supports)

    def beam_total_analysis(self):
        """Uses beam_analysis to find max moment, shear for loads, and find max deflection for service & live loads"""
        #Find max moment and shear using total loads, print moment and shear graphs
        self.M_vert, self.V_vert, _, self.M_max, self.bending_stress, self.V_max, self.shear_stress, _, self.total_supports = self.beam_analysis(self.loads, self.pt_loads, None)
        #Find max service deflection using service loads, as well as calculated reactions at supports using service loads, print displacement
        _, _, self.service_defl_vert, _, _, _, _, self.service_defl_max, self.service_supports = self.beam_analysis(self.service_loads, self.service_pt_loads, "Service Loads", show_plots = False)

        #Find max live load deflection using live loads, as well as calculated reactions at supports using live loads, print displacement
        _, _, self.live_defl_vert, _, _, _, _, self.live_defl_max, self.live_supports = self.beam_analysis(self.live_loads, self.live_pt_loads, "Live Loads",  show_plots = False)

    def beam_analysis(self, loads, pt_loads, load_label,show_plots=True):
        """Takes beam parameters and returns moment, shear, and deflection in beam"""
        # supports is list of lists with x or y values relative to beam starting (forces will be added as second list item at end). moments added as third item if necessary.
        # if not specified, supports will be assumed to be pinned
        # pt__loads is list of lists with x or y values rel to beam start, and force (positive is downwards)
        # loads is list of uniform loads with start, end, and load (positive is downwards)

        #Creates support_holder list object (that will be edited) based on initial supports
        support_holder = copy.deepcopy(self.supports)

        # Create Loads objects out of loads list
        uniform_loads = []
        if len(loads) >= 1:
            for i in loads:
                uniform_loads.append(Loads(i[0], i[1], i[2]))

        # Organize uniform_loads & combine overlapping uniform_loads
        uniform_loads.sort(key = lambda x: x.start)

        # Create array new_loads to hold new combined loads created from overlapping loads
        new_loads = []

        # Find overlapping loads, add values to create new load, and trim old load lengths
        for index, i in enumerate(uniform_loads):
            if index < len(uniform_loads) - 1:
                if uniform_loads[index].end > uniform_loads[index + 1].start:
                    if uniform_loads[index].end < uniform_loads[index + 1].end:
                        org_end = uniform_loads[index].end
                        org_plus_start = uniform_loads[index + 1].start
                        uniform_loads[index].end = org_plus_start
                        uniform_loads[index + 1].start = org_end
                        new_loads.append(Loads(org_plus_start, org_end, uniform_loads[index].load + uniform_loads[index + 1].load))
                    if uniform_loads[index].end > uniform_loads[index + 1].end:
                        org_end = uniform_loads[index].end
                        org_plus_start = uniform_loads[index + 1].start
                        org_plus_end = uniform_loads[index + 1].end
                        org_load = uniform_loads[index].load
                        org_plus_load = uniform_loads[index + 1].load
                        uniform_loads[index].end = org_plus_start
                        uniform_loads[index + 1].start = org_plus_end
                        uniform_loads[index + 1].end = org_end
                        uniform_loads[index + 1].load = org_load
                        new_loads.append(Loads(org_plus_start, org_plus_end, org_load + org_plus_load))
                if uniform_loads[index].start == uniform_loads[index + 1].start:
                    if uniform_loads[index].end > uniform_loads[index + 1].end:
                        org_end = uniform_loads[index].end
                        org_plus_start = uniform_loads[index + 1].start
                        org_plus_end = uniform_loads[index + 1].end
                        org_load = uniform_loads[index].load
                        org_plus_load = uniform_loads[index + 1].load
                        uniform_loads[index].end = org_plus_end
                        uniform_loads[index].load = org_load + org_plus_load
                        uniform_loads[index + 1].start= org_plus_end
                        uniform_loads[index + 1].load = org_load
                    if uniform_loads[index].end < uniform_loads[index + 1].end:
                        org_end = uniform_loads[index].end
                        org_load = uniform_loads[index].load
                        org_plus_load = uniform_loads[index + 1].load
                        uniform_loads[index].load = org_load + org_plus_load
                        uniform_loads[index + 1].start= org_end
                if uniform_loads[index].end == uniform_loads[index + 1].end and uniform_loads[index].start < uniform_loads[index + 1].start:
                    org_end = uniform_loads[index].end
                    org_plus_start = uniform_loads[index + 1].start
                    org_plus_end = uniform_loads[index + 1].end
                    org_load = uniform_loads[index].load
                    org_plus_load = uniform_loads[index + 1].load
                    uniform_loads[index].end = org_plus_start
                    uniform_loads[index + 1].load = org_load + org_plus_load
                if uniform_loads[index].end == uniform_loads[index + 1].end and uniform_loads[index].start == uniform_loads[index + 1].start:
                    org_load = uniform_loads[index].load
                    org_plus_load = uniform_loads[index + 1].load
                    uniform_loads[index].load = org_load + org_plus_load
                    del(uniform_loads[index + 1])
        
        #Combine uniform_loads and new_loads array
        total_loads = uniform_loads + new_loads
        total_loads.sort(key = lambda x: x.start)
        
        EI = self.param['E'] * self.param['Ix']       # Flexural rigidity (Elastic modulus * Moment of inertia)

        breakpoints = []
        for i in total_loads:
            breakpoints.append(i.start)
            breakpoints.append(i.end)

        for i in support_holder:
            breakpoints.append(i[0])
        
        for i in self.pt_loads:
            breakpoints.append(i[0])

        # Create a string of symbol names, e.g., 'a b c ...'
        symbol_names = ' '.join([chr(i) for i in range(ord('a'), ord('z') + 1) if chr(i) != 'x'])
        x = sp.symbols('x')

        # Create symbols
        symbols = sp.symbols(symbol_names)
        symbol_count = 0

        # Breakpoints array holds start and end of loads, supports, and pt_load locations
        breakpoints = sorted(set(breakpoints))

        # Array of shear functions along x-axis, at intervals broken by breakpoints
        functions = []

        constants_array = []

        # Add unknown forces to support
        for i in support_holder:
            i[1] = symbols[symbol_count]
            constants_array.append(i[1])
            symbol_count += 1
        # Add unkown moment to support if fixed
        for i in support_holder:
            if i[2] == "Fixed":
                i[2] = symbols[symbol_count]
                constants_array.append(i[2])
                symbol_count += 1
            else:
                i.pop(2)

        count = 1
        for index, i in enumerate(breakpoints):
            if count < len(breakpoints):
                function = 0
                for load in total_loads:
                    if load.start < breakpoints[index + 1]:
                        if load.end < breakpoints[index + 1]:
                            function += (load.end - load.start) * load.load
                        else:
                            function += (x - load.start) * load.load
                for load in pt_loads:
                    if load[0] < breakpoints[index + 1]:
                        function += load[1]
                for support in support_holder:
                    # Exclude last support from shear calcs
                    if support[0] < breakpoints[index + 1]:
                        function += support[1]
                functions.append(function)
            count += 1     

        sys_eq = []
        boundary_conditions = []

        for index, i in enumerate(functions):
            # Integrate w3 to get w2, w1, and w0, adding constants to array
            w3 = sp.nsimplify(i/EI)
            w2 = sp.nsimplify(sp.integrate(w3, x) + symbols[symbol_count])
            constants_array.append(symbols[symbol_count])
            symbol_count += 1
            w1 = sp.nsimplify(sp.integrate(w2, x) + symbols[symbol_count])
            constants_array.append(symbols[symbol_count])
            symbol_count += 1
            w0 = sp.nsimplify(sp.integrate(w1, x) + symbols[symbol_count])
            constants_array.append(symbols[symbol_count])
            symbol_count += 1
            sys_eq.append([w0, w1, w2, w3])

            # Boundary condition at first segment
            if index == 0:
                # If support is fixed, slope is 0 at start 
                if len(support_holder[0]) == 3:
                    boundary_conditions.append(sp.nsimplify(sp.Eq(w1.subs(x, 0), 0,)))

                # If support is pinned, moment is 0 at start
                else:
                    boundary_conditions.append(sp.nsimplify(sp.Eq(w2.subs(x, 0), 0,)))
            
            # Boundary condition at end segment
            if index == len(functions) - 1:
                support_tracker = 0
                for j in support_holder:
                    # If support at end, displacement is 0
                    if j[0] ==  self.length:
                        boundary_conditions.append(sp.nsimplify(sp.Eq(w0.subs(x, self.length), 0,)))
                        # If support is fixed, slope is 0 at end
                        if len(j) == 3:
                            boundary_conditions.append(sp.nsimplify(sp.Eq(w1.subs(x, self.length), 0,)))
                        # If support pinned, moment is 0 at end
                        else:
                            boundary_conditions.append(sp.nsimplify(sp.Eq(w2.subs(x, self.length), 0,)))
                        support_tracker += 1
                # If no support at end, moment = 0
                if support_tracker == 0:
                    boundary_conditions.append(sp.nsimplify(sp.Eq(w2.subs(x, self.length), 0,)))

            # Boundary condition at support_holder (displacement = 0)
            for j in support_holder:
                if breakpoints[index] == j[0]:
                    boundary_conditions.append(sp.nsimplify(sp.Eq(w0.subs(x, j[0]), 0,)))
        
        count = 1
        if len(sys_eq) > 1:
            for index, i in enumerate(sys_eq):
                if index < len(sys_eq) - 1:
                    # Boundary condition for continuity (slope & displacement & moment)
                    boundary_conditions.append(sp.nsimplify(sp.Eq(i[0].subs(x, breakpoints[index + 1]) - sys_eq[index + 1][0].subs(x, breakpoints[index + 1]),0, ),))
                    boundary_conditions.append(sp.nsimplify(sp.Eq(i[1].subs(x, breakpoints[index + 1]) - sys_eq[index + 1][1].subs(x, breakpoints[index + 1]),0, ),))
                    boundary_conditions.append(sp.nsimplify(sp.Eq(i[2].subs(x, breakpoints[index + 1]) - sys_eq[index + 1][2].subs(x, breakpoints[index + 1]),0, ),))
        
        # Equilibirum equations

        # Moment equilibrium
        sum_mom_start = 0
        for i in support_holder:
            sum_mom_start += i[0] * i[1]
            #Add applied moment to moment sum if support is fixed
            if len(i) == 3:
                sum_mom_start += i[2]
        for i in pt_loads:
            sum_mom_start += i[0] * i[1]
        for i in total_loads:
            sum_mom_start += (i.end - i.start) * i.load * ((i.end - i.start)/2 + i.start)
        
        #Moment equilibirum at start
        boundary_conditions.append(sp.Eq(sum_mom_start, 0))

        # If necessary, y-dir force equilibrium
        if len(boundary_conditions) < len(constants_array):
            sum_force_start = 0

            for i in support_holder:
                sum_force_start += i[1]
            for i in pt_loads:
                sum_force_start += i[1]
            for i in total_loads:
                sum_force_start += i.load * (i.end - i.start)

            #Force equilibirum at start
            boundary_conditions.append(sp.Eq(sum_force_start, 0))
    
        # Solve for constants
        constants = sp.solve(boundary_conditions, constants_array)
        # Substitute constants back into eqn
        for i in sys_eq:
            i[0] = i[0].subs(constants)
            i[1] = i[1].subs(constants)
            i[2] = i[2].subs(constants)
            i[3] = i[3].subs(constants)

        x_vals = np.linspace(0,self.length,100)

        equations = []
        for index, i in enumerate(sys_eq):
            w_func = sp.lambdify(x, i[0], modules=['numpy', 'sympy'])
            M_func = sp.lambdify(x, i[2] * EI, modules=['numpy', 'sympy'])
            V_func = sp.lambdify(x, i[3] * EI, modules=['numpy', 'sympy'])
            equations.append([])
            equations[index].append(w_func)
            equations[index].append(V_func)
            equations[index].append(M_func)
        
        # Evaluate the expressions over the range
        displacement_vals = []
        moment_vals = []
        shear_vals = []
        total_x_vals = []

        interval = 20
        for index, i in enumerate(breakpoints):
            if index < len(breakpoints) - 1:
                x_vals = np.linspace(i, (breakpoints[index + 1]), interval)

                if isinstance(equations[index][0](x_vals), np.ndarray):
                    displacement_vals.extend(equations[index][0](x_vals))
                else:
                    displacement_vals.extend([equations[index][0](x_vals)] * interval)

                if isinstance(equations[index][1](x_vals), np.ndarray):
                    shear_vals.extend(equations[index][1](x_vals))
                else:
                    shear_vals.extend([equations[index][1](x_vals)] * interval)

                if isinstance(equations[index][2](x_vals), np.ndarray):
                    moment_vals.extend(equations[index][2](x_vals))
                else:
                    moment_vals.extend([equations[index][2](x_vals)] * interval)

                total_x_vals.extend(x_vals)

        beam_shape = []
        for i in total_x_vals:
            beam_shape.append(0)

        if show_plots:
        
            # Moment plot
            plt.subplot(2, 1, 1)
            plt.plot(total_x_vals, moment_vals, label="Moment")
            plt.xlabel("Position along the beam (in)")
            plt.ylabel("Moment (kip-in)")
            plt.title("Beam Moment")
            plt.grid(True)
            plt.legend()
            
            # Shear plot
            plt.subplot(2, 1, 2)
            plt.plot(total_x_vals, shear_vals, label="Shear")
            plt.xlabel("Position along the beam (in)")
            plt.ylabel("Shear (kips)")
            plt.title("Beam Shear")
            plt.grid(True)
            plt.legend()
        
            plt.tight_layout()
            plt.show()
        
        else:
            # Displacement plot
            plt.subplot(1, 1, 1)
            plt.plot(total_x_vals, displacement_vals, label=str(load_label + " Displacement (in)"))
            plt.xlabel("Position along the beam (in)")
            plt.ylabel("Displacement")
            plt.title("Beam Displacement")
            plt.grid(True)
            plt.legend()
            plt.show()

        #Attach to beam

        M_vert = []
        V_vert = []
        defl_vert = []

        M_max = max(moment_vals, key=abs)
        V_max = max (shear_vals, key=abs)
        defl_max = max (displacement_vals, key=abs)

        for index, i in enumerate (moment_vals):
            M_vert.append([total_x_vals[index],i])
        for index, i in enumerate (shear_vals):
            V_vert.append([total_x_vals[index], i])
        for index, i in enumerate (displacement_vals):
            defl_vert.append([total_x_vals[index], i])
        

        # Add forces to support_holder
        for i in support_holder:
            i[1] = i[1].subs(constants)

        bending_stress = M_max / self.param["Sx"]
        shear_stress = V_max / self.param["A"]

        return (M_vert, V_vert, defl_vert, M_max, bending_stress, V_max, shear_stress, defl_max, support_holder)