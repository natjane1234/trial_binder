# Find max moment, shear etc.. in beam

import sympy as sp
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import ast
from .materials import alum, sections_data, wood_data, alum_sections

class Loads:
    """Assigns parameters to different load objects."""
   
    def __init__(self, start, end, load):
        self.start = start
        self.end = end
        self.load = load


# supports is list of lists with x or y values relative to beam starting (only simple supports) (forces will be added as second list item at end)
# pt__loads is list of lists with x or y values rel to beam start, and force (positive is downwards)
# loads is list of uniform loads with start, end, and load (positive is downwards)

def beam_analysis(length, material, shape, supports, pt_loads, loads, show_plots=True):
    """Takes beam parameters and returns moment, shear, and deflection in beam"""

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
    
    EI = E * Ix       # Flexural rigidity (Elastic modulus * Moment of inertia)

    breakpoints = []
    for i in total_loads:
        breakpoints.append(i.start)
        breakpoints.append(i.end)

    for i in supports:
        breakpoints.append(i[0])
    
    for  i in pt_loads:
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

    # Add unknown forces to supports
    for i in supports:
        i[1] = symbols[symbol_count]
        constants_array.append(i[1])
        symbol_count += 1

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
            for support in supports:
                # Exclude last support from shear calcs
                if support[0] < breakpoints[index + 1]:
                    function += support[1]
            functions.append(function)
        count += 1     


    EI = E * Ix
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

        # Boundary condition at first segment- moment 0 at start
        if index == 0:
            boundary_conditions.append(sp.nsimplify(sp.Eq(w2.subs(x, 0), 0,)))
        
        # Boundary condition at end segment- moment = 0, displacement = 0 if support
        if index == len(functions) - 1:
            boundary_conditions.append(sp.nsimplify(sp.Eq(w2.subs(x, length), 0,),))
            for j in supports:
                if j[0] ==  length:
                    boundary_conditions.append(sp.nsimplify(sp.Eq(w0.subs(x, length), 0,)))

        # Boundary condition at supports (displacement = 0)
        for j in supports:
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
        
    sum_mom_start = 0

    for i in supports:
        sum_mom_start += i[0] * i[1]
    for i in pt_loads:
        sum_mom_start += i[0] * i[1]
    for i in total_loads:
        sum_mom_start += (i.end - i.start) * i.load * ((i.end - i.start)/2 + i.start)
    
    boundary_conditions.append(sp.nsimplify(sp.Eq(sum_mom_start, 0)))
 
    # Solve for constants
    constants = sp.solve(boundary_conditions, constants_array)
    
    # Substitute constants back into eqn
    for i in sys_eq:
        i[0] = i[0].subs(constants)
        i[1] = i[1].subs(constants)
        i[2] = i[2].subs(constants)
        i[3] = i[3].subs(constants)

    x_vals = np.linspace(0,length,100)

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
        # Displacement plot
        plt.subplot(3, 1, 1)
        plt.plot(total_x_vals, displacement_vals, label="Displacement")
        plt.plot(total_x_vals, beam_shape, label="Beam")
    
    
        plt.xlabel("Position along the beam (in)")
        plt.ylabel("Displacement")
        plt.title("Beam Displacement")
        plt.grid(True)
        plt.legend()
    
        # Moment plot
        plt.subplot(3, 1, 2)
        plt.plot(total_x_vals, moment_vals, label="Moment")
        plt.xlabel("Position along the beam (in)")
        plt.ylabel("Moment (kip-in)")
        plt.title("Beam Moment")
        plt.grid(True)
        plt.legend()
        
        # Shear plot
        plt.subplot(3, 1, 3)
        plt.plot(total_x_vals, shear_vals, label="Shear")
        plt.xlabel("Position along the beam (in)")
        plt.ylabel("Shear (kips)")
        plt.title("Beam Shear")
        plt.grid(True)
        plt.legend()
    
        plt.tight_layout()
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
    

    # Add forces to supports
    for i in supports:
        i[1] = i[1].subs(constants)

    #Export parameters
    parameters = {
        "Parameter": ["Depth", "Width", "Thickness", "Ix", "Sx", "E", "A"],
        "Value": [round(depth,1), round(width,2), thickness, round(Ix,1), round(Sx,1), round(E,0), round(A,2)],
        "Unit": ["in", "in", "in", "in^4", "in^3", "ksi", "in^2"]
    }

    bending_stress = M_max / Sx
    shear_stress = V_max / A
    
    param_data = pd.DataFrame(parameters)
    param_data.set_index('Parameter', inplace = True)
    return (M_vert, V_vert, defl_vert, M_max, bending_stress, V_max, shear_stress, defl_max, supports, param_data)







    

 