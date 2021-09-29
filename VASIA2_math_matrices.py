import numpy as np
import numpy.ma as ma
import time
from osgeo import gdal, gdalconst, osr
import os

work_folder = r'E:\IKI\Microwave_data\SSMIS\NSIDC-0032-v2\20130915'
epsg_file = r'E:\IKI\Microwave_data\GIS\EPSG_3408.txt'
os.chdir(work_folder)

fn_19V = r'EASE-F17-NL2013258.19V.bin'
fn_19H = r'EASE-F17-NL2013258.19H.bin'

fn_37V = r'EASE-F17-NL2013258.37V.bin'
fn_37H = r'EASE-F17-NL2013258.37H.bin'

fn_85V = r'EASE-F17-NL2013258.91V.bin'
fn_85H = r'EASE-F17-NL2013258.91H.bin'


# Read binary as array
def read_binary(file_name):
    dataset = gdal.Open(file_name)
    ds_array = dataset.GetRasterBand(1).ReadAsArray()
    return ds_array


# Convert to real Brightness temperatures
def convert2temps(int_vals):
    # T_vals = int_vals / 10            # Uncomment if values are not normalized
    # T_vals[T_vals == 0] = np.nan      # Uncomment if values are not normalized
    # return T_vals                     # Uncomment if values are not normalized
    int_vals[int_vals == 0] = np.nan
    return int_vals


# Add 3rd dimention
def add_dim(arr2d):
    return np.expand_dims(arr2d, axis=2)


# Raed binary and add extra dim for each file
T19V = add_dim(convert2temps(read_binary(fn_19V)))
T19H = add_dim(convert2temps(read_binary(fn_19H)))
T37V = add_dim(convert2temps(read_binary(fn_37V)))
T37H = add_dim(convert2temps(read_binary(fn_37H)))
T85V = add_dim(convert2temps(read_binary(fn_85V)))
T85H = add_dim(convert2temps(read_binary(fn_85H)))


# Calculate tg: tg(85-37 H)
def tan85_37h(p85h, p37h):
    return (p85h - p37h) / (85.5 - 37)


# Calculate tg: tg(85-19 V)
def tan85_19v(p85v, p19v):
    return (p85v - p19v) / (85.5 - 19.35)


# Calculate tg: tg(37-19 V)
def tan37_19v(p37v, p19v):
    return (p37v - p19v) / (37 - 19.35)


# Set linear function for F1 (85H and 37H)
def f85_37h(I):
    return -0.085 * I + 0.908


# Set linear function for F1 (85V and 19V)
def f85_19v(I):
    return -0.086 * I + 0.55


# Set linear function for F2 (85H and 37H)
def phi85_37h(I):
    return -0.039 * I + 1.19


# Set linear function for F2 (85V and 19V)
def phi85_19v(I):
    return -0.04 * I + 0.7


# Make a range of concentrations from 0% to 100% (in tenths)
I = np.arange(0, 10.1, 0.1)


# Set function #1
def F1(I, T85H, T37H, T85V, T19V):
    return 0.5 * ((f85_37h(I) - tan85_37h(T85H, T37H)) ** 2 / tan85_37h(T85H, T37H) ** 2 + (
                f85_19v(I) - tan85_19v(T85V, T19V)) ** 2 / tan85_19v(T85V, T19V) ** 2)


def F2(I, T85H, T37H, T85V, T19V):
    return 0.5 * ((phi85_37h(I) - tan85_37h(T85H, T37H)) ** 2 / tan85_37h(T85H, T37H) ** 2 + (
                phi85_19v(I) - tan85_19v(T85V, T19V)) ** 2 / tan85_19v(T85V, T19V) ** 2)


# Set linear function for checking puddles
def delta37_19v(I_min):
    return -0.187 * I_min + 1.1


def I1_to_I2(i1, i2, tg37_19v):
    if delta37_19v(i1) < tg37_19v:
        return i1
    # elif delta37_19v(i1) >= tg37_19v:
    else:
        return i2


def array2raster(filename, upper_left_X, upper_left_Y, Xres, Yres, cols, rows, array):
    driver = gdal.GetDriverByName('ENVI')
    outRaster = driver.Create(filename, cols, rows, 1, gdal.GDT_Float32)
    outRaster.SetGeoTransform((upper_left_X, Xres, 0, upper_left_Y, 0, Yres))
    outband = outRaster.GetRasterBand(1)
    outband.WriteArray(array)
    outRasterSRS = osr.SpatialReference()
    f = open(epsg_file, "r")
    wkt = f.read()
    outRasterSRS.ImportFromWkt(wkt)
    outRaster.SetProjection(outRasterSRS.ExportToWkt())
    outband.FlushCache()


vectI1_to_I2 = np.vectorize(I1_to_I2)

start = time.time()

I1_min = np.argmin(F1(I, T85H, T37H, T85V, T19V), axis=2) / 10
I2_min = np.argmin(F2(I, T85H, T37H, T85V, T19V), axis=2) / 10

result = vectI1_to_I2(I1_min, I2_min, tan37_19v(T37V, T19V)[:, :, 0])

"""
print (I1_min[673, 821])
print (I2_min[673, 821])
print(result[673, 821])

print("time required for vectorized form computations: {round(time.time() - start, 2)}, s")


result_pixel_by_pixel = np.zeros_like(result)
result_pixel_by_pixel.shape

start = time.time()
for i in range(1441):
  for j in range(1441):
    pixel = i, j
    F1_0 = F1(I, T85H[pixel], T37H[pixel], T85V[pixel], T19V[pixel])
    F2_0 = F2(I, T85H[pixel], T37H[pixel], T85V[pixel], T19V[pixel])
    I1_min_pixel = np.argmin(F1_0, axis=0) / 10
    I2_min_pixel = np.argmin(F2_0, axis=0) / 10
    result_pixel_by_pixel[i, j] = I1_to_I2(I1_min_pixel, I2_min_pixel, tan37_19v(T37V[pixel], T19V[pixel]))

print("time required for cyclic computations: {round(time.time() - start, 2)}, s")

np.count_nonzero(result == result_pixel_by_pixel) == result.shape[0] * result.shape[1]
print(result[0, :])


for i in range(1441):
    for j in range(1441):
        F1_0 = F1(I, T85H[i][j], T37H[i][j], T85V[i][j], T19V[i][j])
        F2_0 = F2(I, T85H[i][j], T37H[i][j], T85V[i][j], T19V[i][j])
        I1_min_pixel = I[np.argmin(F1_0, axis=0)]
        I2_min_pixel = I[np.argmin(F2_0, axis=0)]
        result[i, j] = I1_to_I2(I1_min_pixel, I2_min_pixel, tan37_19v(T37V[i][j], T19V[i][j]))
"""

row = 673
col = 821
ulx_25km = -9036842.76
uly_25km = 9036842.76
xRes_25km = 25067.525
yRes_25km = -25067.525
Cols_25km = 721
Rows_25km = 721

result_mask = np.where(result > 0, 1, 0)  # Create mask to exclude false puddles
# I1_min_maked = ma.masked_values(I1_min, 0)
# I2_min_maked = ma.masked_values(I2_min, 0)
I2_I1 = (result - I1_min) * result_mask

array2raster('vasia2_ice_conc.bin', ulx_25km, uly_25km, xRes_25km, yRes_25km, Cols_25km, Rows_25km, result)
# array2raster('vasia2_ice_concD_mask.bin', ulx_25km, uly_25km, xRes_25km, yRes_25km, Cols_25km, Rows_25km, result_mask)
array2raster('I2-I1.bin', ulx_25km, uly_25km, xRes_25km, yRes_25km, Cols_25km, Rows_25km, I2_I1)
# array2raster('I1D.bin', ulx_25km, uly_25km, xRes_25km, yRes_25km, Cols_25km, Rows_25km, I1_min)
# array2raster('I2D.bin', ulx_25km, uly_25km, xRes_25km, yRes_25km, Cols_25km, Rows_25km, I2_min)


