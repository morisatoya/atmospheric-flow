from re import A
import sys

from pyproj import transform
sys.path.append ('C:\\Users\\Python\\Lib\site-packages')
import netCDF4
from netCDF4 import Dataset
import numpy as np
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import simplekml

data = Dataset('D:\\PythonData\\MERRA2_400.tavg1_2d_slv_Nx.20231101.nc4',mode='r')

def get(atr):
        return data.variables[atr]

def get_uv(atr):
       return(get('U'+atr), get('V'+atr))

def fill_with_nan(x):
        x_nans = x[:]; x_nans[x==x._FillValue]=0
        return x_nans

def make_ws(u, v):
        u_nans = fill_with_nan(u); v_nans =fill_with_nan(v)
        wind_speed = np.sqrt(u_nans**2+v_nans**2)
        return (u_nans, v_nans, wind_speed)

def draw_map(u, V, c, s, s_height, is_draw_map, filename):
        fig = plt.figure(figsize=(40,40),facecolor='black')
        ax = plt.axes(projection=ccrs.NearsidePerspective(central_longitude=137.0, central_latitude=0, satellite_height=s_height, false_easting=0, false_northing=0, globe=None))
        if is_draw_map:
            ax.add_feature(cfeature.OCEAN)
            ax.add_feature(cfeature.LAND)
            ax.add_feature(cfeature.LAKES)
            ax.add_feature(cfeature.RIVERS)
            ax.add_feature(cfeature.BORDERS)
            ax.coastlines(resolution="110m", linewidth=1)
            ax.gridlines(linestyle='--', color='black')
        qv = plt.quiver(lon, lat, u, v, c, transform=ccrs.PlateCarree(),scale=s, alpha=1.0, cmap='coolwarm')
        fig.savefig(filename, format='png', dpi=120)
        
winds = [{'height':"2M", 'file':"2M.png", 'map':True, 'scale':200, 'alt_in_m':2},
               {'height':"850", 'file':"850.png", 'map':True, 'scale':200, 'alt_in_m':1500},
               {'height':"500", 'file':"500.png", 'map':True, 'scale':200, 'alt_in_m':5500},
               {'height':"250", 'file':"250.png", 'map':True, 'scale':200, 'alt_in_m':14000}]

s = 2
lon, lat = np.meshgrid(get('lon'), get('lat'))
lon = lon[::s,::s]; lat = lat[::s,::s]

for w in winds:
       u, v = get_uv(w['height']); u, v, ws = make_ws(u, v) 
       u = u[0,::s,::s]; 
       v = v[0,::s,::s];
       ws = ws[0,::s,::s]
       draw_map(u, v, ws, w['scale'], 100000000000, w['map'], w['file'])
       
def dstLatLon(lat, lon, heading, l):
    lat0 = l/(40000*1000)*360
    lon0 = l/(40000*1000)*360/np.cos(lat)
    lat0 = lat0*np.cos(heading)
    lon0 = lon0*np.sin(heading)
    return lat+lat0, lon+lon0

f = open('wind.kml', 'w')
f.write("<?xml version='1.0' encoding='UTF-8'?>\n")
f.write("<kml xmlns='http://earth.google.com.kml/2.2'>\n")
f.write("<Document>\n <name>flight</name>\n")

for k, w in enumerate(winds):
    u, v = get_uv(w['height']); u, v, ws =make_ws(u, v)
    u = u[0,::s,::s];
    v = v[0,::s,::s];
    ws =ws[0,::s,::s]
    alt = w['alt_in_m']*10
    for i in range(lon.shape[0]):
        for j in range(lon.shape[1]):
             color = int(np.clip(10*int(ws[i,j]),0,255))
             lat_d, lon_d = dstLatLon(lat[i,j], lon[i,j], np.pi/2-np.arctan2(v[i,j], u[i,j]), ws[i,j]*10000)
             f.write("<Placemark>\n        <TimeSpan>\n        <begin>" + '2023-11-01T00:00:00' + "</begin>\n        <LineStyle>\n")
             f.write("     <Style>\n    <LineStyle>\n")
             f.write("     <color>40" + '%02x%02x%02x'%(0,255-color,color) + "</color>\n")
             f.write("    <width>5</width>\n     </LineStyle>\n")
             f.write("     </Style>\n     <LineString>\n")
             f.write("            <extrude>0</extrude>\n")
             f.write("            <altitudeMode>absolute</altitudeMode>\n")
             f.write("             <coordinates>" + str(lon[i,j]) + "," + str(lat[i,j]) + "," + str(alt) + " " + str(lon_d) + "," + str(lat_d) + "," + str(alt) + "</coordinates>\n")
f.write("</Document></kml>\n");

f.close()