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