import qgis # already loaded
import processing # idem
import os # file management
from osgeo import gdal, osr # raster input/output
import numpy as np

myfolder=r'C:\Users\mlc\Downloads'
# load auxiliary functions
myscriptsfolder=r'C:\Users\mlc\Documents\PyQGIS\scripts'
exec(open(os.path.join(myscriptsfolder,'auxiliary_functions.py').encode('utf-8')).read())


# my constants
fn=os.path.join(myfolder,'wc2.1_30s_prec_12.tif')
newfn=os.path.join(myfolder,      'cropped12.tif')
newln='cropped01'
fn=os.path.join(myfolder,'COSsim_2020M21_N3_v0_TM06_TNE.tif')
newfn=os.path.join(myfolder,'UnidTerrit.tif')
newln='UnidTerrit'
# project and data set CRS
my_crs=QgsCoordinateReferenceSystem(3763)
# crop to, in fn coordinates
(myxMin,myxMax,myyMin,myyMax) = (-10,-5,36,43)
(myxMin,myyMin,myxMax,myyMax) = (-46726,35894,-34456,49506)

##################################################### project; add layers
# Create project
myproject,mycanvas= my_clean_project()

# set project CRS
myproject.setCrs(my_crs)

rlayer=my_add_raster_layer(fn,'01')

###################################################### gdal & numpy

# access file
gdal_layer = gdal.Open(fn, gdal.GA_ReadOnly) 

# fetch parameters from rlayer (that will be needed to convert processed data back to QgsRasterLayer)
# determine coordinate transformation with gdal
geotransform = gdal_layer.GetGeoTransform()   # from osgeo.gdal.Dataset object
# determine no data value from data provider
nodatavalue=rlayer.dataProvider().sourceNoDataValue(1) # should be float
# nan can not be converted to integer
if not np.isnan(nodatavalue):
    nodatavalue=int(rlayer.dataProvider().sourceNoDataValue(1)) # from QgsRasterLayer object

# check:
## Get nodata value from the GDAL band object
#nodata = band.GetNoDataValue()
#
##Create a masked array for making calculations without nodata values
#rasterArray = np.ma.masked_equal(rasterArray, nodata)
#type(rasterArray)
#
## Check again array statistics
#rasterArray.min()


# determine raster size
W=rlayer.width() # from QgsRasterLayer object
H=rlayer.height() # from QgsRasterLayer object
# determine CRS
EPSGcode=int(rlayer.crs().authid()[5:]) # from QgsRasterLayer object

#if not EPSGcode==4326: stop # below use lat/long to crop

############################### process data with numpy and write results to new raster
# (1) convert data to numpy array and process
# Reading a chunk of a GDAL band into a numpy array. https://gdal.org/python/osgeo.gdal.Dataset-class.html#ReadAsArray
# real original raster as numpy array
my_array=gdal_layer.ReadAsArray() 
(H,W)=my_array.shape
if not H==rlayer.height() or not W==rlayer.width(): stop

## convert nodatavalues into numpy.nan
#if not np.isnan(nodatavalue):
#    my_array[my_array==nodatavalue]=np.nan

# change array dimension by cropping it

xMin=rlayer.extent().xMinimum()
xMax=rlayer.extent().xMaximum()
yMin=rlayer.extent().yMinimum()
yMax=rlayer.extent().yMaximum()

# resolutions
rx=geotransform[1]
ry=geotransform[5] # negative
# rows and columns to crop
colMin=int(np.floor((myxMin-xMin)/rx))
colMax=int(np.ceil((myxMax-xMin)/rx))
rowMin=int(np.floor((myyMax-yMax)/ry))
rowMax=int(np.ceil((myyMin-yMax)/ry))

# crop array
my_new_array=my_array[rowMin:rowMax, colMin:colMax]
newH=my_new_array.shape[0]
newW=my_new_array.shape[1]
new_geotransform=list(geotransform)
new_geotransform[0]=geotransform[0]+colMin*rx
new_geotransform[3]=geotransform[3]+rowMin*ry
new_geotransform=tuple(new_geotransform)

# (1) create empty raster with gdal using parameters above
my_new_raster=None
my_new_raster = gdal.GetDriverByName('GTiff').Create(newfn,newW,newH,1,gdal.GDT_Float32) # or bandreference.DataType
my_new_raster.SetGeoTransform(new_geotransform)
srs=osr.SpatialReference()
srs.ImportFromEPSG(EPSGcode)
my_new_raster.SetProjection(srs.ExportToWkt())

# (2) write processed data to my_raster
my_new_raster.GetRasterBand(1).WriteArray(my_new_array)
# assign original nodatavalue to my_new_raster
my_new_raster.GetRasterBand(1).SetNoDataValue(nodatavalue)

# close connection
my_new_raster = None

# load new raster
my_rlayer=iface.addRasterLayer(newfn,newln)

# what is the no data value for the new raster
my_rlayer.dataProvider().sourceNoDataValue(1)

