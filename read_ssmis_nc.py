from osgeo import gdal

# Path of netCDF file
nc_file = "W_XX-ESA_SMOS_CS2_NH_25KM_EASE2_20210106_20210112_o_v203_01_l4sit.nc"

# Specify the layer name to read
layer_name = "cryosat_sea_ice_thickness"

# Open netcdf file.nc with gdal
ds = gdal.Open("NETCDF:{0}:{1}".format(nc_file, layer_name))


#ds_list = gdal.Open(nc_file.GetSubDatasets())
#print(ds)


# Read full data from netcdf
data = ds.ReadAsArray(0, 0, ds.RasterXSize, ds.RasterYSize)
data[data < 0] = 0

import matplotlib.pyplot as plt
plt.imshow(data)
plt.show()
