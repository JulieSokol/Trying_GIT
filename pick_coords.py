import numpy as np
from osgeo import osr, gdal
from pyproj import  Transformer



infile = r'E:\IKI\Microwave_data\SSMIS\NSIDC-0032-v2\20130815\EASE-F17-NL2013227.19V.bin'

""""
#Lat Long value
long = 70.3558
lat = 74.8735


transformer = Transformer.from_crs("epsg:4326", "epsg:3408", always_xy=True)
x,y = transformer.transform(long, lat)
print(x, y)
"""
x = 324040.8914747575763613
y = 707643.62154488288797438

indataset = gdal.Open(infile)
indataset.GetRasterBand(1)

cols = indataset.RasterXSize
rows = indataset.RasterYSize

transform = indataset.GetGeoTransform()

xOrigin = transform[0] # X of the upper left corner of the image
yOrigin = transform[3] # Y of the upper left corner of the image
pixelWidth = transform[1] # X dimetion of the pixel resolution
pixelHeight = -transform[5] # Y dimetion of the pixel resolution
data = indataset.ReadAsArray(0, 0, cols, rows)


col = int((x - xOrigin) / pixelWidth)
row = int((yOrigin - y) / pixelHeight)
print (row,col)
value = data[row][col]
print (value)

x_pix = (col * pixelWidth + xOrigin) + pixelWidth/2
y_pix = (yOrigin - row * pixelHeight) - pixelHeight/2
print(x_pix, y_pix)









