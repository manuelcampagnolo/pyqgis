# read AF in csv format download from FIRMS; 

#################################### import
import qgis # already loaded
import processing # idem
import os # file management
import numpy as np # numpy, for arrays, etc
from urllib.parse import urljoin #path2uri
import urllib.request
from qgis.PyQt.QtCore import QVariant # types for attributes in vector layers
from PyQt5.QtWidgets import (QWidget, QPushButton, QLineEdit, QInputDialog, QApplication, QLabel)
from haversine import haversine, Unit, inverse_haversine, Direction
from math import pi
from datetime import datetime as dt
import pandas as pd


parent=iface.mainWindow() # necessary for QMessageBox

# DATA and FUNCTIONS FOLDERS: ADAPT
myfolder=r'C:\Users\mlc\OneDrive - Universidade de Lisboa\Documents\investigacao-projectos-reviews-alunos\SIRESP'
folderfunctions=r'C:\Users\mlc\OneDrive - Universidade de Lisboa\Documents\scripts_gee_py_R\scripts_python_functions'

# load auxiliary functions
exec(open(os.path.join(folderfunctions,'auxiliary_functions.py').encode('utf-8')).read())


#
## input file Monchique 2018
#list_fn_viirs = [os.path.join(myfolder,'monchique_2018','DL_FIRE_SV-C2_278445','fire_archive_SV-C2_278445.csv')]
#list_fn_modis = [os.path.join(myfolder,'monchique_2018','DL_FIRE_M-C61_278444','fire_archive_M-C61_278444.csv')]
#  
## portugal julho 2022
#fa_folder=os.path.join(myfolder,'Europa_julho_2022')
#list_ln_viirs=os.listdir(fa_folder)
#list_fn_viirs=[os.path.join(myfolder,'Europa_julho_2022',f) for f in list_ln_viirs]
#
# Serra estrela Agosto 2022
fn_npp=os.path.join(myfolder,'firms','fire_archive_SV-C2_25686.csv')
fn_noaa=os.path.join(myfolder,'firms','fire_nrt_J1V-C2_25685.csv')
fn_modis=os.path.join(myfolder,'firms','fire_nrt_M-C61_25687.csv')

list_fn_viirs = [fn_npp,fn_noaa]
list_fn_modis = [fn_modis]

#clear layer tree and canvas and creates instance of project
myproject,mycanvas = my_clean_project()

# main options
K=1 # footprint size
INPUT_VIIRS=True
INPUT_MODIS=True
CREATE_AF_FROM_CSV=True
EXISTING_FILE=NULL
EXISTING_FILE=os.path.join(myfolder,'firms','fa_portugal_agosto_2022_viirs_modis.gpkg')
CREATE_LAYER_FOOTPRINTS=True
CREATE_LEGEND_MODIS=False
CREATE_LEGEND_VIIRS=False
if CREATE_LAYER_FOOTPRINTS or CREATE_LEGEND_MODIS or CREATE_LEGEND_VIIRS:
    PROCESS_FOOTPRINTS=True
else: 
    PROCESS_FOOTPRINTS=False
PROCESS_ISOCRONAS=False

# my remaining constants
ln_viirs ='viirs' 
ln_viirs_day='viirs_day'
ln_modis ='modis' 
ln_modis_day='modis_day'
ln_af='af'
#fn_isocronas = os.path.join(myfolder,'isocronas_monchique','ISOCRONAS_MONCHIQUE_v3.shp')
#ln_isocronas='isocronas'
#ln_isocronas_new='isocronas_new'
#ln_isocronas_diss= 'isocronas_day_int'
## Attributes
an_frp='frp'
an_track='track'
an_scan='scan'
an_bright='brightness'
#an_isocronas='DIA_HORA'
# new attributes
an_day="day" # decimal day
an_day_int="day_int" # integer day
an_foot='footprint'
an_frpkm2="frpkm2"
an_size='size' # chose which
# track inclinations (azimuth) for Portugal
orbit_modis_terra=193
orbit_viirs=orbit_modis_aqua=346
# study area 
fn_studyArea= os.path.join(myfolder,'CAOP','Cont_AAD_CAOP2020.gpkg')
# CAOP_2020_dissolve.gpkg
fn_studyArea= os.path.join(myfolder,'CAOP','CAOP_2020_dissolve.gpkg')
ln_studyArea='CAOP'

option_size=an_frpkm2 # create 'size' attribute for footprints


# study area
my_add_vector_layer(fn_studyArea,ln_studyArea)
#mylayer=my_processing_run("native:dissolve",ln_studyArea,{},ln_studyArea+'_diss')

if CREATE_AF_FROM_CSV:
    ######################  read and process csv table with lon, lat coordinates
    # parameters to read csv file (some options)
    #params='?delimiter=%s&xField=%s&yField=%s' % (",", "Lon", "Lat")
    #sep=';'
    #params="?delimiter={}&detectTypes=yes&geomType=none".format(sep)
    #params="?delimiter=;&detectTypes=yes&geomType=none"
    params='?delimiter=%s&xField=%s&yField=%s' % (",", "longitude", "latitude")
    # uri for reading the file as "delimitedtext"
    MYLAYERS=[]
    ln_viirs_list=[]
    ln_modis_list=[]
    if INPUT_VIIRS:
        for fn_viirs in list_fn_viirs:
            ln_viirs=os.path.basename(os.path.splitext(fn_viirs)[0])
            uri='file:///'+fn_viirs+params
            mylayer = QgsVectorLayer(uri, '', "delimitedtext")
            mylayer.setName(ln_viirs)
            mylayer.setCrs(QgsCoordinateReferenceSystem(4326))
            myproject.addMapLayer(mylayer)
            MYLAYERS.append(ln_viirs)
            ln_viirs_list.append(ln_viirs)
    if INPUT_MODIS:
        for fn_modis in list_fn_modis:
            ln_modis=os.path.basename(os.path.splitext(fn_modis)[0])
            uri='file:///'+fn_modis+params
            mylayer = QgsVectorLayer(uri, '', "delimitedtext")
            mylayer.setName(ln_modis)
            mylayer.setCrs(QgsCoordinateReferenceSystem(4326))
            myproject.addMapLayer(mylayer)
            MYLAYERS.append(ln_modis)
            ln_modis_list.append(ln_modis)
    # merge viirs and modis and create point vector layer 
    # "native:mergevectorlayers", {'LAYERS':[
    dict_params={'LAYERS': MYLAYERS}
    mylayer=my_processing_run("native:mergevectorlayers",'',dict_params,ln_af+'_all')
    # select study area
    dict_params={'OVERLAY': ln_studyArea}
    mylayer=my_processing_run("native:clip",ln_af+'_all',dict_params,ln_af)
    
    # remove previous layer
    if INPUT_VIIRS: 
        for ln_viirs in ln_viirs_list: my_remove_layer(ln_viirs)
    if INPUT_MODIS: 
        for ln_modis in ln_modis_list: my_remove_layer(ln_modis)
elif EXISTING_FILE!=NULL:
    mylayer=my_add_vector_layer(EXISTING_FILE,ln_af)
else: 
    stop
