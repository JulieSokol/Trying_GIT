import numpy as np
from osgeo import gdal, gdalconst, osr
import os
import shutil
import re
import glob

work_folder = r'E:\IKI\Microwave_data\SSMIS\NSIDC-0032-v2\20130915'
grid_25km = r'E:\IKI\Microwave_data\GIS\EASE_N25km.hdr'
grid_12_5km = r'E:\IKI\Microwave_data\GIS\EASE_N12.5km.hdr'
epsg_file = 'E:\IKI\Microwave_data\GIS\EPSG_3408.txt'

os.chdir(work_folder)

######### Initial preprocessing: 1. setting extension  ##################
for i in os.listdir():
    if i[-4:] == '.bin' or  i[-4:] == '.hdr':
        print('Файл уже имеет какое-то расширение', i)
        continue
    else:
        os.rename(i, i+'.bin')
        print('Файл без разширения', i)

######### Initial preprocessing: 2. setting HDR- files ##################
for i in os.listdir():
    if 'NL' in i:
        if os.path.exists(os.path.join(i[:-4]+'.hdr')):
            print('HDR file  already exists')
        else:
            shutil.copyfile(grid_25km, os.path.join(work_folder, i[:-4]+'.hdr'))
    elif 'NH' in i:
        if os.path.exists(os.path.join(i[:-4]+'.hdr')):
            print('HDR file  already exists')
        else:
            shutil.copyfile(grid_12_5km, os.path.join(work_folder, i[:-4] + '.hdr'))

#########################################################################
########################  Basic functions ###############################
#########################################################################

 # Function for reading dataset to numpy array
def read_binary (file_name):
    dataset = gdal.Open(file_name)
    ds_array = dataset.GetRasterBand(1).ReadAsArray()
    return  ds_array

# Function for making resulting file names
def set_new_fn (file_name):
    parsed_fn_name = re.findall(r'EASE-F(\d{2})-N(\w)(\d{7})(A|D)\S*.(\d{2})(V|H).bin', file_name)
    new_fn_mosaic = 'EASE-F'+parsed_fn_name[0][0] + '-N' + parsed_fn_name[0][1] + parsed_fn_name[0][2] + parsed_fn_name[0][3]+ '.' + parsed_fn_name[0][4] + parsed_fn_name[0][5] + '.bin'
    new_fn_high_res = 'EASE-F'+parsed_fn_name[0][0] + '-N' + 'H' + parsed_fn_name[0][2] + parsed_fn_name[0][3]+ '.' + parsed_fn_name[0][4] + parsed_fn_name[0][5] + '.bin'
    return new_fn_mosaic, new_fn_high_res



# Function for merging accending and descending passes into one mosaic, and conversion values to Kelvin (division by 10)
def to_Kelvin (ChannelX):
    ChannelX_Kelvin = ChannelX / 10
    ChannelX_Kelvin[ChannelX_Kelvin == 0] = np.nan
    return ChannelX_Kelvin

# Function, where we set parameters for grid transformations
def set_resampling_parameters (upper_left_X, upper_left_Y, Xres, Yres, cols, rows):
    ulx = upper_left_X
    uly = upper_left_Y
    lrx = ulx + (cols * Xres)
    lry = uly + (rows * Yres)
    output_extent = [ulx, lry, lrx, uly]  # Create extent
    return output_extent

"""
# Function for transformation 25 km grid to 12.5 km
def resample_25km_to_12km (filename, im_25km, Xres, Yres, extent):
    #im_12km = gdal.Warp('EASE-F13-NH1996271-V2.19V.tif',im_25km, xRes=Xres, yRes=Yres, outputBounds = extent, resampleAlg = gdalconst.GRA_Average)
    #im_12km = gdal.Warp('', im_25km, format = 'VRT', xRes=Xres, yRes=Yres, outputBounds=extent,resampleAlg=gdalconst.GRA_Average)
    im_12km = gdal.Warp(filename, im_25km, format = 'ENVI', xRes=Xres, yRes=Yres, outputBounds=extent,resampleAlg=gdalconst.GRA_Average)
    return im_12km
"""
# Function for saving resulting numpy array to raster
def array2raster(filename,upper_left_X, upper_left_Y, Xres, Yres, cols, rows, array):
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


###############################################################################
############################# Process Data ####################################
###############################################################################

############## Set files to variables: matching by mask ########################
file_list = os.listdir()
for f in file_list:
    if re.match(r'EASE-F\d{2}-N\w\d{7}(A)\S*.(19)(V).bin', f): A19V_fn = f
    elif re.match(r'EASE-F\d{2}-N\w\d{7}(A)\S*.(19)(H).bin', f): A19H_fn = f
    elif re.match(r'EASE-F\d{2}-N\w\d{7}(D)\S*.(19)(V).bin', f): D19V_fn = f
    elif re.match(r'EASE-F\d{2}-N\w\d{7}(D)\S*.(19)(H).bin', f): D19H_fn = f
    elif re.match(r'EASE-F\d{2}-N\w\d{7}(A)\S*.(37)(V).bin', f): A37V_fn = f
    elif re.match(r'EASE-F\d{2}-N\w\d{7}(A)\S*.(37)(H).bin', f): A37H_fn = f
    elif re.match(r'EASE-F\d{2}-N\w\d{7}(D)\S*.(37)(V).bin', f): D37V_fn = f
    elif re.match(r'EASE-F\d{2}-N\w\d{7}(D)\S*.(37)(H).bin', f): D37H_fn = f
    elif re.match(r'EASE-F\d{2}-NH\d{7}(A)\S*.(85)(V).bin', f): A85V_fn = f
    elif re.match(r'EASE-F\d{2}-NH\d{7}(A)\S*.(85)(H).bin', f): A85H_fn = f
    elif re.match(r'EASE-F\d{2}-NH\d{7}(D)\S*.(85)(V).bin', f): D85V_fn = f
    elif re.match(r'EASE-F\d{2}-NH\d{7}(D)\S*.(85)(H).bin', f): D85H_fn = f
    else: pass

############ Group files for further bulk processing #############################
LR_files = [A19V_fn, D19V_fn], [A19H_fn, D19H_fn], [A37V_fn, D37V_fn], [A37H_fn, D37H_fn]
HR_files = [A85V_fn, D85V_fn], [A85H_fn, D85H_fn]


####### Set parameters for 25 km and 12.5 km grids ######
################### 25 km grid ##########################
ulx_25km = -9036842.76
uly_25km = 9036842.76
xRes_25km = 25067.525
yRes_25km = -25067.525
Cols_25km = 721
Rows_25km = 721
################### 12.5 km grid #######################
ulx_12km = -9030574.08
uly_12km = 9030574.08
xRes_12km = 12533.76
yRes_12km = -12533.76
Cols_12km = 1441
Rows_12km = 1441

####################### Processing low resolution channels ########################
######## Make a mosaic from 25 km rasters and then resample it to 12.5 km grid ####

for i in LR_files:
    RasterA  = read_binary(i[0])   # Read raster, consisting of ascending passes
    RasterD = read_binary(i[1])    # Read raster, consisting of descending passes
    mosaic_AD = to_Kelvin_and_mosaic(RasterA, RasterD)   # Make a mosaic from Raster A and D
    extent_25km = set_resampling_parameters(ulx_25km, uly_25km, xRes_25km, yRes_25km, Cols_25km,
                                            Rows_25km)  # set and calculate extra parameteres for a 12.5km grid
    new_name_mosaic, new_name_hr = set_new_fn(i[0])     # Configure filename for outputs
    array2raster(new_name_mosaic, ulx_25km, uly_25km, xRes_25km, yRes_25km, Cols_25km, Rows_25km, mosaic_AD) # Save array to raster
    mos_25km = gdal.Open(new_name_mosaic)  # Open saved raster
    mos_25km.GetRasterBand(1)   # Take first band of the opened raster
    extent_12km = set_resampling_parameters(ulx_12km, uly_12km, xRes_12km, yRes_12km, Cols_12km,
                                            Rows_12km)  # set and calculate extra parameteres for a 12.5km grid
    resampled_mosaic = resample_25km_to_12km(new_name_hr, mos_25km, xRes_12km, yRes_12km, extent_12km)  # Resample 25 km raster to 12.5 km raster

####################### Processing low resolution channels ########################
####################### Make a mosaic from 12.5 km rasters ########################

for i in HR_files:
    RasterA  = read_binary(i[0]) # Read raster, consisting of ascending passes
    RasterD = read_binary(i[1])  # Read raster, consisting of descending passes
    mosaic_AD = to_Kelvin_and_mosaic(RasterA, RasterD) # Make a mosaic from Raster A and D
    extent_12km = set_resampling_parameters(ulx_12km, uly_12km, xRes_12km, yRes_12km, Cols_12km,
                                            Rows_12km)  # set and calculate extra parameteres for a 12.5km grid
    new_name_mosaic, new_name_hr = set_new_fn(i[0])  # Configure filename for outputs
    array2raster(new_name_hr, ulx_12km, uly_12km, xRes_12km, yRes_12km, Cols_12km, Rows_12km, mosaic_AD) # Save array to raster
"""
