#loads should be uniform over beam length, kips per inch
def udl_cantilever (length, load, E, I, Sx, A):
    max_moment = load * length**2 / 2
    bending_stress = max_moment / Sx
    max_shear = load * length
    shear_stress = max_shear / A
    max_deflection = load * length**4 /24 / E / I 
    return max_moment, max_shear, max_deflection, bending_stress, shear_stress

    