import pandas as pd
from importlib.resources import files
from .materials import sections_data, wood_data

data_folder = files('tools.data')

df = pd.read_csv(data_folder / 'mod_factors.csv')
df = df.set_index('Modification Factor')

# Note: if a mod factor does not apply to a paramter, that factor is not effected here, but automatically set as 1.00 for the purposes of calculations
# Function to update DataFrame view based on dropdown selection

def mod_factors(shape, length, material, wet_service, temp, stability, size_factor, flat_use, curvature, incising, repetitive, format, resistance_factor):

    #Mod factors for glulam
    if (material == "1.5E LVL" or material == "2.0E LVL" or material == "2.2E LVL"):
        # Wet service factors
        if wet_service == 'Wet service':
            df.loc["Wet Service", "Fb"] = 0.8
            df.loc["Wet Service", "Fv"]  = 0.875
            df.loc["Wet Service", "Fc"]  = 0.73
            df.loc["Wet Service", "FcP"]  = 0.53
            df.loc["Wet Service", "E"]  = 0.833
            df.loc["Wet Service", "Emin"]  = 0.833
        else:
            df.loc["Wet Service", "Fb"] = 1.00
            df.loc["Wet Service", "Fv"]  = 1.00
            df.loc["Wet Service", "Fc"]  = 1.00
            df.loc["Wet Service", "FcP"]  = 1.00
            df.loc["Wet Service", "E"]  = 1.00
            df.loc["Wet Service", "Emin"]  = 1.00
    
        # Temperature factor (NDS Table 2.3.3)
        if temp == 'Elevated (100 degrees F < T <= 125 degrees F)':
            df.loc["Temperature", "Emin"]  = 0.9
            df.loc["Temperature", "E"]  = 0.9 
            if wet_service == 'EMC exceeds 19':
                df.loc["Temperature", "Fb"] = 0.7
                df.loc["Temperature", "Fv"]  = 0.7
                df.loc["Temperature", "Fc"]  = 0.7
                df.loc["Temperature", "FcP"]  = 0.7
            else:
                df.loc["Temperature", "Fb"] = 0.8
                df.loc["Temperature", "Fv"]  = 0.8
                df.loc["Temperature", "Fc"]  = 0.8
                df.loc["Temperature", "FcP"]  = 0.8
        elif temp == 'Elevated (above 125 degrees F)':
            df.loc["Temperature", "E"]  = 0.9
            df.loc["Temperature", "Emin"]  = 0.9
            if wet_service == 'EMC exceeds 19':
                df.loc["Temperature", "Fb"] = 0.5
                df.loc["Temperature", "Fv"]  = 0.5
                df.loc["Temperature", "Fc"]  = 0.5
                df.loc["Temperature", "FcP"]  = 0.5
            else:
                df.loc["Temperature", "Fb"] = 0.7
                df.loc["Temperature", "Fv"]  = 0.7
                df.loc["Temperature", "Fc"]  = 0.7
                df.loc["Temperature", "FcP"]  = 0.7
        else:
            df.loc["Temperature", "E"]  = 1.00
            df.loc["Temperature", "Emin"]  = 1.00
            df.loc["Temperature", "Fb"] = 1.00
            df.loc["Temperature", "Fv"]  = 1.00
            df.loc["Temperature", "Fc"]  = 1.00
            df.loc["Temperature", "FcP"]  = 1.00
            
        # Stability factor
        if stability == 'Discontinuous Lateral Support':
            df.loc["Beam Stability", "Fb"] = "See NDS"
        else:
            df.loc["Beam Stability", "Fb"] = 1.00

        #This is technically volume factor, but need to add extra row
        x = 10
        df.loc["Size", "Fb"] = round(min((21/length)**(1/x)*(12/sections_data.loc[shape]["d"])**(1/x)*(5.125/sections_data.loc[shape]["b"])**(1/x),1.0),2)

        # Flat_use factor
        if flat_use == 'Weak axis bending':
            df.loc["Flat Use", "Fb"] = "See NDS"
        else:
            df.loc["Flat Use", "Fb"] = 1.00
    
        # No incising factor, keep mod at 1.00
        df.loc["Incising", "Fb"] = 1.00
        df.loc["Incising", "Fv"]  = 1.00
        df.loc["Incising", "Fc"]  = 1.00
        df.loc["Incising", "FcP"]  = 1.00
        df.loc["Incising", "E"]  = 1.00
        df.loc["Incising", "Emin"]  = 1.00

        # No repetitive factor, keep mod at 1.00
        df.loc["Repetitive Member", 'Fb'] = 1.00
        
        # Column stability factor automatically calculated with column calcs
    
        # Buckling stiffness factor excluded (conservative for Emin)
        # Bearing area factor excluded (assuming length not under 6")

        # Stress interaction excluded (assuming not tapered)
        # Shear reduction factor excluded, check 5.3.10 for applications
        
        # Curvature factor
        if curvature == 'Curved':
            df.loc["Curvature", "Fb"] = "See NDS"
            df.loc["Curvature", "Fv"]  = "See NDS"
            df.loc["Curvature", "Fc"]  = "See NDS"
            df.loc["Curvature", "FcP"]  = "See NDS"
            df.loc["Curvature", "E"]  = "See NDS"
            df.loc["Curvature", "Emin"]  = "See NDS"
        else:
            df.loc["Curvature", "Fb"] = 1.00
            df.loc["Curvature", "Fv"]  = 1.00
            df.loc["Curvature", "Fc"]  = 1.00
            df.loc["Curvature", "FcP"]  = 1.00
            df.loc["Curvature", "E"]  = 1.00
            df.loc["Curvature", "Emin"]  = 1.00
            
    else:    
        # Wet service factors
        if wet_service == 'EMC exceeds 19':
            df.loc["Wet Service", "Fb"] = 0.85
            df.loc["Wet Service", "Fv"]  = 0.97
            df.loc["Wet Service", "Fc"]  = 0.8
            df.loc["Wet Service", "FcP"]  = 0.67
            df.loc["Wet Service", "E"]  = 0.9
            df.loc["Wet Service", "Emin"]  = 0.9
        else:
            df.loc["Wet Service", "Fb"] = 1.00
            df.loc["Wet Service", "Fv"]  = 1.00
            df.loc["Wet Service", "Fc"]  = 1.00
            df.loc["Wet Service", "FcP"]  = 1.00
            df.loc["Wet Service", "E"]  = 1.00
            df.loc["Wet Service", "Emin"]  = 1.00
    
        # Temperature factor (NDS Table 2.3.3)
        if temp == 'Elevated (100 degrees F < T <= 125 degrees F)':
            df.loc["Temperature", "Emin"]  = 0.9
            df.loc["Temperature", "E"]  = 0.9 
            if wet_service == 'EMC exceeds 19':
                df.loc["Temperature", "Fb"] = 0.7
                df.loc["Temperature", "Fv"]  = 0.7
                df.loc["Temperature", "Fc"]  = 0.7
                df.loc["Temperature", "FcP"]  = 0.7
            else:
                df.loc["Temperature", "Fb"] = 0.8
                df.loc["Temperature", "Fv"]  = 0.8
                df.loc["Temperature", "Fc"]  = 0.8
                df.loc["Temperature", "FcP"]  = 0.8
        elif temp == 'Elevated (above 125 degrees F)':
            df.loc["Temperature", "E"]  = 0.9
            df.loc["Temperature", "Emin"]  = 0.9
            if wet_service == 'EMC exceeds 19':
                df.loc["Temperature", "Fb"] = 0.5
                df.loc["Temperature", "Fv"]  = 0.5
                df.loc["Temperature", "Fc"]  = 0.5
                df.loc["Temperature", "FcP"]  = 0.5
            else:
                df.loc["Temperature", "Fb"] = 0.7
                df.loc["Temperature", "Fv"]  = 0.7
                df.loc["Temperature", "Fc"]  = 0.7
                df.loc["Temperature", "FcP"]  = 0.7
        else:
            df.loc["Temperature", "E"]  = 1.00
            df.loc["Temperature", "Emin"]  = 1.00
            df.loc["Temperature", "Fb"] = 1.00
            df.loc["Temperature", "Fv"]  = 1.00
            df.loc["Temperature", "Fc"]  = 1.00
            df.loc["Temperature", "FcP"]  = 1.00
            
        # Stability factor
        if stability == 'Discontinuous Lateral Support':
            df.loc["Beam Stability", "Fb"] = "See NDS"
        else:
            df.loc["Beam Stability", "Fb"] = 1.00
    
        #Size factor looked up automatically from tables 
        df.loc["Size", "Fb"] = float(sections_data.loc[shape, "CF_bending"])
        df.loc["Size", "Fc"] = float(sections_data.loc[shape, "CF_comp"])
    
        # Flat_use factor
        if flat_use == 'Weak axis bending':
            df.loc["Flat Use", "Fb"] = "See NDS"
        else:
            df.loc["Flat Use", "Fb"] = 1.00
                    # Flat_use factor
        if flat_use == 'Weak axis bending':
            df.loc["Flat Use", "Fb"] = "See NDS"
        else:
            df.loc["Flat Use", "Fb"] = 1.00
    
        # Incising factor
        if incising == 'Incised':
            df.loc["Incising", "Fb"] = 0.8
            df.loc["Incising", "Fv"]  = 0.8
            df.loc["Incising", "Fc"]  = 0.8
            df.loc["Incising", "FcP"]  = 1.00
            df.loc["Incising", "E"]  = 0.95
            df.loc["Incising", "Emin"]  = 0.95
        else:
            df.loc["Incising", "Fb"] = 1.00
            df.loc["Incising", "Fv"]  = 1.00
            df.loc["Incising", "Fc"]  = 1.00
            df.loc["Incising", "FcP"]  = 1.00
            df.loc["Incising", "E"]  = 1.00
            df.loc["Incising", "Emin"]  = 1.00
            
        # Repetitive factor
        if repetitive == 'Repetitive':
            df.loc["Repetitive Member", 'Fb'] = 1.15
        else:
            df.loc["Repetitive Member", 'Fb'] = 1.00
    
        # Column stability factor automatically calculated with column calcs
    
        # Buckling stiffness factor excluded (conservative for Emin)
        # Buckling area factor excluded (conservative for Fcp)
    return df



