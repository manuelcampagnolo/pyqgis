# Dados Serra Estrela 2022 Siresp

import qgis # already loaded
import processing # idem
import os # file management
import requests # to add xyz layer
from osgeo import ogr # connection to geopackage
import re
import rasterio
from rasterio.warp import reproject, Resampling, calculate_default_transform # reproject with rasterio
from osgeo import gdal # 
from osgeo.gdalconst import GA_Update # no data
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
import datetime as dt
import numpy as np
# basemaps
import xyzservices.providers as xyz
xyz.keys()
# xyz.CartoDB.Positron.url

# DATA and FUNCTIONS FOLDERS: ADAPT
myfolder=r'C:\Users\mlc\OneDrive - Universidade de Lisboa\Documents\investigacao-projectos-reviews-alunos\SIRESP'
folderfunctions=r'C:\Users\mlc\OneDrive - Universidade de Lisboa\Documents\scripts_gee_py_R\scripts_python_functions'

# load auxiliary functions
exec(open(os.path.join(folderfunctions,'auxiliary_functions.py').encode('utf-8')).read())

############################################################# project, canvas, etc
parent=iface.mainWindow() # necessary for QMessageBox

# project and data set CRS
my_crs=3763
# Create project
myproject,mycanvas= my_clean_project()
# Define root (layers and groups)
myroot = myproject.layerTreeRoot()
myroot.clear() # Clear any information from this layer tree (layers and groups)
bridge = QgsLayerTreeMapCanvasBridge(myroot, mycanvas)
# set project CRS
myproject.setCrs(QgsCoordinateReferenceSystem(my_crs))

############################################################  dados

fn_siresp = os.path.join(myfolder,'Historico6a20AgostoFiltrado_csv_time_utf8.csv')
ln_siresp ='siresp' #  

fn_fa=os.path.join(myfolder,'firms','fa_portugal_agosto_2022_viirs_modis.csv')
ln_fa='fa'

# street maps
uri_StreetMap = 'type=xyz&url=https://a.tile.openstreetmap.org/%7Bz%7D/%7Bx%7D/%7By%7D.png&zmax=19&zmin=0&crs=EPSG3857'
iface.addRasterLayer(uri_StreetMap, "OpenStreetMap", "wms")

######################  read and process a non-spatial table
#
# convert data to utf-8 if they use a different encoding 
if False:
    convert_encoding_to_utf8(fn_siresp)

# read file with pandas
df=pd.read_csv(fn_siresp,sep=";")
selected=['DEVICE_ID', 'SIGNAL_DATE', 'Unnamed: 3', 'LONG', 'LAT','SIGNAL_DATE_END', 'Unnamed: 11', 'TIPO', 'DESCRICAO_TIPO','DISTINCTDEVICE_IDs']
newnames=['DEVICE_ID', 'date_start' , 'time_start', 'LONG', 'LAT','date_end',         'time_end',    'TIPO', 'DESCRICAO_TIPO','DISTINCTDEVICE_IDs']
df=df[selected]
df.columns=newnames

# create datetime variables
df['dt_start']=df['date_start']+' '+df['time_start']
df['dt_start_str'] = pd.to_datetime(df['dt_start'], format='%d/%m/%Y %H:%M:%S').dt.strftime('%Y-%m-%d %H:%M:%S')
df['dt_start'] = pd.to_datetime(df['dt_start'], format='%d/%m/%Y %H:%M:%S')
df['dt_end']=df['date_end']+' '+df['time_end']
df['dt_end_str'] = pd.to_datetime(df['dt_end'], format='%d/%m/%Y %H:%M:%S').dt.strftime('%Y-%m-%d %H:%M:%S')
df['dt_end'] = pd.to_datetime(df['dt_end'], format='%d/%m/%Y %H:%M:%S')
df['dif_m']=(df['dt_end']-df['dt_start'])/dt.timedelta(minutes=1) #).astype(int)
df.dtypes

# day frequencies
df.dt_start.dt.day.value_counts().sort_index()

# select record by day
df=df[df.dt_start.dt.day > 14]

# select columns 
selected=['DEVICE_ID', 'dt_start_str', 'dt_end_str', 'dif_m','LONG', 'LAT', 'TIPO', 'DESCRICAO_TIPO','DISTINCTDEVICE_IDs']
df=df[selected]

# convert to geopandas
gdf = gpd.GeoDataFrame(df, geometry=gpd.points_from_xy(df.LONG, df.LAT))

# convert to layer
# json doesn't handle Timestamp objects by default
mylayer = QgsVectorLayer(gdf.to_json(),ln_siresp,"ogr")
QgsProject.instance().addMapLayer(mylayer)

########################################################## FA
# read file with pandas
df=pd.read_csv(fn_fa,sep=",")
# create datetime variable


####################################################### canvas
# extent
mycanvas.setExtent(mylayer.extent())
mycanvas.refresh()

# legend for dif_m
# output: a dictionary where keys are the class labels
# each dict value is (minClass,maxClass,QColor,myopacity)

breaks=[2,5,10,30,60,120,240,1000000]
mydict=create_custom_graduated_legend_dict(breaks,colormap='YlOrRd',myopacity=0.9,units='m')
create_graduated_legend(mylayer,'dif_m',mydict)
