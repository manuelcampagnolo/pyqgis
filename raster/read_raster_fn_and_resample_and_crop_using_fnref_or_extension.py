import qgis # already loaded
import processing # idem
import os # file management
from osgeo import gdal, osr, gdalconst # raster input/output, resampling
import numpy as np


myfolder=r'C:\Users\mlc\Downloads\Dados_Trabalho_Arronches'
myscriptsfolder=r'C:\Users\mlc\Documents\PyQGIS\scripts'
exec(open(os.path.join(myscriptsfolder,'auxiliary_functions.py').encode('utf-8')).read())

# project and data set CRS
my_crs=3763
# Create project
myproject,mycanvas= my_clean_project()
# set project CRS
myproject.setCrs(QgsCoordinateReferenceSystem(my_crs))

# my constants
# input file
fn=os.path.join(myfolder,'PREC.tif')
fn=os.path.join(myfolder,'dem_aw3d_pt_25m.tif')
# fn_new=os.path.join(myfolder,'aux.tif')
# reference file for resampling
fn_ref=os.path.join(myfolder,'COSsimCONC.tif') # reference != original
#fn_ref=os.path.join(myfolder,'cropped01.tif') # reference=original
# output file
fn_out=os.path.join(myfolder,'PREC10m.tif')
fn_out=os.path.join(myfolder,'MDE10m.tif')
ln='input'
ln_out='resampled'
nbands=1

##rlayer=my_add_raster_layer(fn,ln)
#
#(array , nodatavalue) = create_array_from_raster_file_name(fn)
#
## (2) Create from fn new empty raster in file fn_new, with nbands number of bands
#create_new_empty_raster_from_filename(fn,fn_new,nbands)
# in alternative try create constant raster from Processing Toolbox
#
## (3) write processed data to file fn_new
## see https://gdal.org/tutorials/raster_api_tut.html#opening-the-file
#dataset = gdal.Open(fn_new, gdal.GA_Update) # open connection
#dataset.GetRasterBand(1).WriteArray(my_array)
## assign original nodatavalue to my_new_raster
#dataset.GetRasterBand(1).SetNoDataValue(nodatavalue)
## close connection
#dataset = None
#
# (4) resample fn_new to fn_out using fn_ref as the new grid
resample_raster_fn_to_fnout_using_fnref(fn,fn_ref,fn_out,nbands=1)

# add layer to project
rlayer=my_add_raster_layer(fn_out,ln_out)

print(rlayer.dataProvider().sourceNoDataValue(1))
