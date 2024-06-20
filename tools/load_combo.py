#Input dictionary of loads, with load combos organized into sub-dictionaries vert & lat
# D, L, Lr, S, R, W, E
def load_combos(loads):
    #Find maximum vetical load, and create dict of vertical load combos 
    vert_loads = {"1.4D": 1.4*loads["D"]["vert"], "1.2D + 1.6L + 0.5(Lr or S or R)": 1.2*loads["D"]["vert"] + 1.6*loads["L"]["vert"] + 0.5*loads["Lr"]["vert"],
                  "1.2D + 1.6(Lr or S or R) + (L or 0.5W)": 1.2*loads["D"]["vert"] + 1.6*loads["Lr"]["vert"] + max(loads["L"]["vert"],0.5*loads["Lr"]["vert"]),
                  "1.2D + 1.0W + L + 0.5(Lr or S or R)": 1.2*loads["D"]["vert"] + 1.0*loads["W"]["vert"] + 1.0*loads["L"]["vert"] + 0.5*loads["Lr"]["vert"],
                  "1.2D + 1.0E + L + 0.2S": 1.2*loads["D"]["vert"] + 1.0*loads["E"]["vert"] + 1.0*loads["L"]["vert"] + 0.2*loads["S"]["vert"],
                  "0.9D + 1.0W": 0.9*loads["D"]["vert"] + 1.0*loads["W"]["vert"], "0.9D + 1.0E": 0.9*loads["D"]["vert"] + 1.0*loads["E"]["vert"]}

    lat_loads = {"1.4D": 1.4*loads["D"]["lat"], "1.2D + 1.6L + 0.5(Lr or S or R)": 1.2*loads["D"]["lat"] + 1.6*loads["L"]["lat"] + 0.5*loads["Lr"]["lat"],
                  "1.2D + 1.6(Lr or S or R) + (L or 0.5W)": 1.2*loads["D"]["lat"] + 1.6*loads["Lr"]["lat"] + max(loads["L"]["lat"],0.5*loads["Lr"]["lat"]),
                  "1.2D + 1.0W + L + 0.5(Lr or S or R)": 1.2*loads["D"]["lat"] + 1.0*loads["W"]["lat"] + 1.0*loads["L"]["lat"] + 0.5*loads["Lr"]["lat"],
                  "1.2D + 1.0E + L + 0.2S": 1.2*loads["D"]["lat"] + 1.0*loads["E"]["lat"] + 1.0*loads["L"]["lat"] + 0.2*loads["S"]["lat"],
                  "0.9D + 1.0W": 0.9*loads["D"]["lat"] + 1.0*loads["W"]["lat"], "0.9D + 1.0E": 0.9*loads["D"]["lat"] + 1.0*loads["E"]["lat"]}

    return(vert_loads, lat_loads)
    
                  
    