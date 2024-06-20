import googlemaps
import requests

# Define your seismic forces function here, modified to take 'address' and 'dead_load' from widget inputs
def seismic_forces(address, dead_load, R):
    """Find wind and seismic parameters for self location."""
    
    # Your API key (be cautious with sharing API keys publicly)
    gmaps = googlemaps.Client(key='AIzaSyCxUeCj9DOAokEPW-vj3JCp_uGDV_EVkIQ')
    location = gmaps.geocode(address)
    lat = location[0]['geometry']['location']['lat']
    lng = location[0]['geometry']['location']['lng']

    x = requests.get(f"https://earthquake.usgs.gov/ws/designmaps/asce7-16.json?latitude={lat}&longitude={lng}&riskCategory=II&siteClass=D&title=Example")
    parameters = x.json()

    sds = parameters['response']['data']['sds']
    s1 = parameters['response']['data']['s1']

    Ie = 1
    g = 32.17
    if(s1 < 0.6 * g):
       Cs = max(sds / R * Ie, 0.044 * sds * Ie, 0.01)
    else:
       Cs = max(sds / R * Ie, 0.044 * sds * Ie, 0.01, 0.5 * s1 / R * Ie)

    V = Cs * dead_load
    redundancy = 1.3
    Eh = V * redundancy
    Ev = 0.2 * sds * dead_load

    return (Cs, Eh, Ev, sds)
