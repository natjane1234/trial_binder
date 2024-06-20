import math
#Wind loads are based ASCE 7-16 Chapter 27: Wind Loads on Buildings:
#Main Wind Force Resisting System(Directional Procedure- Part 1).
#Pressure applied simultaneously to windward and leeward walls.
#Length is measured parallel to ridge line.

#Wind load for simple gable roof building, wind parallel to ridge line(double check applies to all)
def wind_load_parr_ridge (V, Kz, Kzt, Kd, Ke, G, height, L, B):
    Cp_wind = 0.8
    qz = 0.0025 * Kz * Kzt * Kd * Ke * V**2
    if (L / B) < 1:
        Cp_lee = -0.5
    elif (L / B) >= 4:
        Cp_lee = -0.2
    else:
        Cp_lee = -0.3

    if (height / L) <= 0.5:
        if L > 2 * height:
            Cp_roof_up = -0.3
        elif L > height:
            Cp_roof_up = -0.5
        else:
            Cp_roof_up = -0.9
    else:
        if L > height / 2:
            Cp_roof_up = -0.7
        else:
            Cp_roof_up = -1.3
    
    p_roof_up = qz * G * Cp_roof_up
    p_windward = qz * G * Cp_wind # lb/ft^2
    p_lee = qz * G * Cp_lee

    return(p_windward, p_lee, p_roof_up)

#Wind load for simple gable roof building, wind perpendicular to ridge line(double check applies to all)
def wind_load_perp_ridge (V, Kz, Kzt, Kd, Ke, G, L, B,Cp_roof_wind_up, Cp_roof_wind_down, Cp_roof_lee_up):
    Cp_wind = 0.8
    qz = 0.0025 * Kz * Kzt * Kd * Ke * V**2
    if (B / L) < 1:
        Cp_lee = -0.5
    elif (B / L) >= 4:
        Cp_lee = -0.2
    else:
        Cp_lee = -0.3

    #Pressure on windward side of building
    p_windward = qz * G * Cp_wind # lb/ft^2

    #Pressure on lee of building
    p_lee = qz * G * Cp_lee

    #Pressure orthogonal to windward roof, downwards
    p_roof_wind_down = qz * G * Cp_roof_wind_down

    #Pressure orthogonal to windward roof, upwards
    p_roof_wind_up = qz * G * Cp_roof_wind_up

    #Pressure orthogonal to lee roof, upwards
    p_roof_lee_up = qz * G * Cp_roof_lee_up

    return(p_windward, p_lee, p_roof_wind_down, p_roof_wind_up, p_roof_lee_up)


