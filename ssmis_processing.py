import sys
import os
from osgeo import gdal, gdalconst
from osgeo.gdalconst import *
import numpy as np


def load_data(file_name, gdal_driver='GTiff'):
    driver = gdal.GetDriverByName(gdal_driver)  ## http://www.gdal.org/formats_list.html
    driver.Register()

    inDs = gdal.Open(file_name, GA_ReadOnly)

    if inDs is None:
        print("Couldn't open this file: %s" % (file_name))
        print(
            '/nPerhaps you need an ENVI .hdr file? A quick way to do this is to just open the binary up in ENVI and one will be created for you.')
        sys.exit("Try again!")
    else:
        print("%s opened successfully" % file_name)

    # Extract some info form the inDs
    geotransform = inDs.GetGeoTransform()

    # Get the data as a numpy array
    band = inDs.GetRasterBand(1)#.SetNoDataValue(0)
    cols = inDs.RasterXSize
    rows = inDs.RasterYSize
    image_array = band.ReadAsArray(0, 0, cols, rows)
    return image_array, (geotransform, inDs)

def array2raster(data_array, geodata, file_out, gdal_driver='GTiff'):
    if not os.path.exists(os.path.dirname(file_out)):
        print("Your output directory doesn't exist - please create it")
        print("No further processing will take place.")
    else:
        post = geodata[0][1]
        original_geotransform, inDs = geodata

        rows, cols = data_array.shape
        bands = 1

        # Set the gedal driver to use
        driver = gdal.GetDriverByName(gdal_driver)
        driver.Register()

        # Creates a new raster data source
        outDs = driver.Create(file_out, cols, rows, bands, gdal.GDT_Float32)

        # Write metadata
        originX = original_geotransform[0]
        originY = original_geotransform[3]

        outDs.SetGeoTransform([originX, post, 0.0, originY, 0.0, -post])
        outDs.SetProjection(inDs.GetProjection())
        #outDs.SetProjection("EPSG:3413")
        #outDs.SetProjection("EPSG:3408")

        # Write raster datasets
        outBand = outDs.GetRasterBand(1)
        outBand.WriteArray(data_array)

        print("Output saved: %s" % file_out)

def to_Kelvin_and_mosaic (mosaicA, mosaicD):
    mosaicA_Kelvin = mosaicA / 10
    mosaicD_Kelvin = mosaicD / 10
    mosaicA_Kelvin[mosaicA_Kelvin == 0] = np.nan
    mosaicD_Kelvin[mosaicD_Kelvin == 0] = np.nan
    mosaic_Kelvin = np.nanmean(np.dstack((mosaicA_Kelvin, mosaicD_Kelvin)), axis=2)
    return mosaic_Kelvin

Bt_A19H="EASE-F17-NL2020306A-V2.19H.bin"
Bt_D19H="EASE-F17-NL2020306D-V2.19H.bin"
Bt_A19H_data, Bt_A19H_geodata=load_data(Bt_A19H, gdal_driver='GTiff')
Bt_D19H_data, Bt_D19H_geodata=load_data(Bt_D19H, gdal_driver='GTiff')
Bt_19H_mosaic = to_Kelvin_and_mosaic(Bt_A19H_data, Bt_D19H_data)
file_out="./EASE-F17-NL2020306-V2.19H.tif" # Write it out as a geotiff
array2raster(Bt_19H_mosaic, Bt_A19H_geodata, file_out, gdal_driver='GTiff')

Bt_A19V="EASE-F17-NL2020306A-V2.19V.bin"
Bt_D19V="EASE-F17-NL2020306D-V2.19V.bin"
Bt_A19V_data, Bt_A19V_geodata=load_data(Bt_A19V, gdal_driver='GTiff')
Bt_D19V_data, Bt_D19V_geodata=load_data(Bt_D19V, gdal_driver='GTiff')
Bt_19V_mosaic = to_Kelvin_and_mosaic(Bt_A19V_data, Bt_D19V_data)
file_out="./EASE-F17-NL2020306-V2.19V.tif" # Write it out as a geotiff
array2raster(Bt_19V_mosaic, Bt_A19V_geodata, file_out, gdal_driver='GTiff')

Bt_A37H="EASE-F17-NL2020306A-V2.37H.bin"
Bt_D37H="EASE-F17-NL2020306D-V2.37H.bin"
Bt_A37H_data, Bt_A37H_geodata=load_data(Bt_A37H, gdal_driver='GTiff')
Bt_D37H_data, Bt_D37H_geodata=load_data(Bt_D37H, gdal_driver='GTiff')
Bt_37H_mosaic = to_Kelvin_and_mosaic(Bt_A37H_data, Bt_D37H_data)
file_out="./EASE-F17-NL2020306-V2.37H.tif" # Write it out as a geotiff
array2raster(Bt_37H_mosaic, Bt_A37H_geodata, file_out, gdal_driver='GTiff')

Bt_A37V="EASE-F17-NL2020306A-V2.37V.bin"
Bt_D37V="EASE-F17-NL2020306D-V2.37V.bin"
Bt_A37V_data, Bt_A37V_geodata=load_data(Bt_A37V, gdal_driver='GTiff')
Bt_D37V_data, Bt_D37V_geodata=load_data(Bt_D37V, gdal_driver='GTiff')
Bt_37V_mosaic = to_Kelvin_and_mosaic(Bt_A37V_data, Bt_D37V_data)
file_out="./EASE-F17-NL2020306-V2.37V.tif" # Write it out as a geotiff
array2raster(Bt_37V_mosaic, Bt_A37V_geodata, file_out, gdal_driver='GTiff')

Bt_A91H="EASE-F17-NH2020306A-V2.91H.bin"
Bt_D91H="EASE-F17-NH2020306D-V2.91H.bin"
Bt_A91H_data, Bt_A91H_geodata=load_data(Bt_A91H, gdal_driver='GTiff')
Bt_D91H_data, Bt_D91H_geodata=load_data(Bt_D91H, gdal_driver='GTiff')
Bt_91H_mosaic = to_Kelvin_and_mosaic(Bt_A91H_data, Bt_D91H_data)
file_out="./EASE-F17-NH2020306-V2.91H.tif" # Write it out as a geotiff
array2raster(Bt_91H_mosaic, Bt_A91H_geodata, file_out, gdal_driver='GTiff')

Bt_A91V="EASE-F17-NH2020306A-V2.91V.bin"
Bt_D91V="EASE-F17-NH2020306D-V2.91V.bin"
Bt_A91V_data, Bt_A91V_geodata=load_data(Bt_A91V, gdal_driver='GTiff')
Bt_D91V_data, Bt_D91V_geodata=load_data(Bt_D91V, gdal_driver='GTiff')
Bt_91V_mosaic = to_Kelvin_and_mosaic(Bt_A91V_data, Bt_D91V_data)
file_out="./EASE-F17-NH2020306-V2.91V.tif" # Write it out as a geotiff
array2raster(Bt_91V_mosaic, Bt_A91V_geodata, file_out, gdal_driver='GTiff')

""""
# Check your output (have a look in QGIS or something)
## by file size...
if os.stat(file_out).st_size == 0:
    print("Doesn't look like the file wrote out properly...")
else:
    print("Output file contains something - plot it or check in GIS")
## or by using your function...
data_check, geodata=load_data(file_out)

"""

"""
import matplotlib.pyplot as plt
plt.imshow(data)
plt.show()
"""