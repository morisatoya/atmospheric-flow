import sys
sys.path.append ('C:\\Users\\Python\\Lib\site-packages')
import netCDF4
from netCDF4 import Dataset
import numpy as np
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature

data = Dataset('D:\\PythonData\\MERRA2_400.tavg1_2d_slv_Nx.20231101.nc4',mode='r')
print(data)
