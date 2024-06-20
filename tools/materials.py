
import pandas as pd
from importlib.resources import files

alum = dict(Ftu = 30, Fty = 25, Fcy = 25, Fsu = 19, E = 10100, Bc = 27.6, Dc = 0.145, Cc = 78, Bp = 31.4, Dp = 0.175, Cp = 74, Bt = 30.5, Dt = 0.978, Ct = 189, Bbr	= 46.1, Dbr	= 0.382, Cbr	= 81, Btb	= 45.7, Dtb	= 2.800, Ctb = 70, Bs = 19.0, Ds = 0.082, Cs = 95
)

#Locate data folder (defined in setup.py)
data_folder = files('tools.data')

sections_data = pd.read_csv(data_folder / 'sections.csv')
sections_data = sections_data.set_index('size')

wood_data = pd.read_csv(data_folder / 'wood_types.csv')
wood_data = wood_data.set_index('species')

alum_sections = pd.read_csv(data_folder / 'geo_data.csv')
alum_sections = alum_sections.set_index('Designation')

