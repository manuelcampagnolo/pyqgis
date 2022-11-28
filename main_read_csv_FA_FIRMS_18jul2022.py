# read AF in csv format download from FIRMS; create footprints; make legend

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

# my working folder
myfolder=r'C:\Users\mlc\OneDrive - Universidade de Lisboa\Documents\profissional-isa-cv\agregacao\aula\dados' # CHANGE
#myfolder=r'C:\Users\mlc\Downloads'
# source auxiliary functions (instead of importing module)
# C:\Users\mlc\OneDrive - Universidade de Lisboa\Documents\Aulas-Cursos\scripts_python
myscriptfolder=r'C:\Users\mlc\OneDrive - Universidade de Lisboa\Documents\Aulas-Cursos\scripts_python' # CHANGE
exec(open(os.path.join(myscriptfolder,'auxiliary_functions.py').encode('utf-8')).read())


# input file Monchique 2018
list_fn_viirs = [os.path.join(myfolder,'monchique_2018','DL_FIRE_SV-C2_278445','fire_archive_SV-C2_278445.csv')]
list_fn_modis = [os.path.join(myfolder,'monchique_2018','DL_FIRE_M-C61_278444','fire_archive_M-C61_278444.csv')]
  
# portugal julho 2022
fa_folder=os.path.join(myfolder,'Europa_julho_2022')
list_ln_viirs=os.listdir(fa_folder)
list_fn_viirs=[os.path.join(myfolder,'Europa_julho_2022',f) for f in list_ln_viirs]
  
#clear layer tree and canvas and creates instance of project
myproject,mycanvas = my_clean_project()

# main options
K=1 # footprint size
INPUT_VIIRS=True
INPUT_MODIS=False
CREATE_AF_FROM_CSV=False
EXISTING_FILE=os.path.join(myfolder,'Europa_julho_2022','viirs_portugal_1_18_julho_2022.gpkg')
CREATE_LAYER_FOOTPRINTS=True
CREATE_LEGEND_MODIS=False
CREATE_LEGEND_VIIRS=False
if CREATE_LAYER_FOOTPRINTS or CREATE_LEGEND_MODIS or CREATE_LEGEND_VIIRS:
    PROCESS_FOOTPRINTS=True
else: 
    PROCESS_FOOTPRINTS=False
PROCESS_ISOCRONAS=False
option_size=an_frpkm2 # create 'size' attribute for footprints

# my remaining constants
ln_viirs ='viirs' 
ln_viirs_day='viirs_day'
ln_modis ='modis' 
ln_modis_day='modis_day'
ln_af='af'
fn_isocronas = os.path.join(myfolder,'isocronas_monchique','ISOCRONAS_MONCHIQUE_v3.shp')
ln_isocronas='isocronas'
ln_isocronas_new='isocronas_new'
ln_isocronas_diss= 'isocronas_day_int'
# Attributes
an_frp='frp'
an_track='track'
an_scan='scan'
an_bright='brightness'
an_isocronas='DIA_HORA'
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

stop

if PROCESS_FOOTPRINTS:
    print(mylayer.dataProvider().fields().names())
    print(mylayer.dataProvider().fields().toList())
    # create new attributes
    pr = mylayer.dataProvider()
    L=[QgsField(an_day, QVariant.Double)] 
    L.append(QgsField(an_day_int,  QVariant.Int))
    L.append(QgsField(an_size,  QVariant.Double))
    L.append(QgsField(an_foot,  QVariant.Double))
    L.append(QgsField(an_frpkm2,  QVariant.Double))
    #L.append(QgsField('ACQ_DATE',  QVariant.String))
    pr.addAttributes(L)
    mylayer.updateFields()
    ## instead, we use a Toolbox function to create a new attribute with NULL values
    ## mylayer = myproject.mapLayersByName(ln_viirs)[0]
    ## print(mylayer.dataProvider().capabilitiesString())
    #dict_params={'FIELD_NAME':an_day,'FIELD_TYPE':1,'FIELD_LENGTH':10,'FIELD_PRECISION':3}
    #mylayer=my_processing_run("native:addfieldtoattributestable",ln_viirs,dict_params,ln_viirs_day)
    #dict_params={'FIELD_NAME':an_size,'FIELD_TYPE':1,'FIELD_LENGTH':10,'FIELD_PRECISION':3}
    #mylayer=my_processing_run("native:addfieldtoattributestable",ln_viirs,dict_params,ln_viirs_day)
    #dict_params={'FIELD_NAME':an_day,'FIELD_TYPE':1,'FIELD_LENGTH':10,'FIELD_PRECISION':3}
    #mylayer=my_processing_run("native:addfieldtoattributestable",ln_modis,dict_params,ln_modis_day)
    #
    # determine max frp/scan*track
    Mfrpkm2,mfrpkm2=0,10**8
    for f in mylayer.getFeatures():
       if  f[an_frp]/(f[an_scan]*f[an_track]) > Mfrpkm2: Mfrpkm2 = f[an_frp]/(f[an_scan]*f[an_track])
       if  f[an_frp]/(f[an_scan]*f[an_track]) < mfrpkm2: mfrpkm2 = f[an_frp]/(f[an_scan]*f[an_track])
#    Mx,mn=0,10**8
#    for f in mylayer.getFeatures():
#       if  f[an_bright] > Mx: Mx= f[an_bright]
#       if  f[an_bright] < mn: mn= f[an_bright]
#    # fill "day" attribute
    with edit(mylayer):
        for f in mylayer.getFeatures():
            # populate an_day
            fa=f['acq_time']
            if isinstance(fa, str): 
                h=float(dt.strptime(fa, '%H:%M:%S').hour)
                m=float(dt.strptime(fa, '%H:%M:%S').minute)
                #h=.hour() #float(np.floor(f['acq_time']/100))
            else:
                h=f['acq_time'].hour()
                m=f['acq_time'].minute()
            #print(h,m)
            #print(float(f['acq_date'].day())+h/24+m/(60*24))
            f[an_day]=float(f['acq_date'].day())+h/24+m/(60*24)
            f[an_day_int]=int(f['acq_date'].day())
            # footprint
            f[an_foot]=f[an_scan]*f[an_track]
            f[an_frpkm2]=f[an_frp]/f[an_foot]        
            # populate an_size
            f[an_size]=1 # omission value
            if option_size==an_bright:
                f[an_size]=1+3*(f[an_bright]-mn)/(Mx-mn)
            if option_size==an_frpkm2:
                f[an_size]=1+3*f[an_frpkm2]/Mfrpkm2
            res=mylayer.updateFeature(f) # to be silent
    # create list of an_day unique values
    pr=mylayer.dataProvider()
    idx=pr.fieldNameIndex(an_day)
    myListValues = list(mylayer.uniqueValues(idx))
    # sort days
    myListValues.sort()
    # create dict for legend
    mydict=create_unary_graduated_legend_dict(values=myListValues,colormap='YlOrRd',myopacity=0.9,decimals=1)
    if CREATE_LEGEND_MODIS:
        dict_params={'EXPRESSION':' "instrument" = \'MODIS\' ','METHOD':0}
        mylayer=my_processing_run("native:extractbyexpression",ln_af,dict_params,'modis')
        create_graduated_legend(mylayer,an_day,mydict,"Square",an_size)
    if CREATE_LEGEND_VIIRS:
        dict_params={'EXPRESSION':' "instrument" = \'VIIRS\' ','METHOD':0}
        mylayer=my_processing_run("native:extractbyexpression",ln_af,dict_params,'viirs')
        create_graduated_legend(mylayer,an_day,mydict,"Circle",an_size)
    #my_remove_layer(ln_af)
    
    if CREATE_LAYER_FOOTPRINTS:
        # vlayer in 4326
        # track and scan in km, orbit in degrees
        def create_footprints(mylayer,K):
            newlayer=QgsVectorLayer("Polygon", "newlayer", "memory")
            pr = newlayer.dataProvider()
            L=[QgsField("longitude", QVariant.Double)]
            L.append(QgsField("latitude",  QVariant.Double))
            L.append(QgsField("scan",  QVariant.Double))
            L.append(QgsField("track",  QVariant.Double))
            L.append(QgsField(an_frp, QVariant.Double))
            L.append(QgsField(an_day_int, QVariant.Int))
            L.append(QgsField('acq_time', QVariant.Int))
            L.append(QgsField('instrument', QVariant.String))
            #ACQ_DATE
            #L.append(QgsField('ACQ_DATE', QVariant.String))
            pr.addAttributes(L)
            newlayer.updateFields() 
            for feat in mylayer.getFeatures():
                track=K*feat['track']
                scan=K*feat['scan']
                if feat['instrument']=='MODIS' and feat['satellite']=='Aqua': orbit=orbit_modis_aqua
                if feat['instrument']=='MODIS' and feat['satellite']=='Terra': orbit=orbit_modis_terra
                if feat['instrument']=='VIIRS': orbit=orbit_viirs
                f=feat.geometry().asPoint()
                lon,lat=f.x(),f.y() # lon, lat of the feature
                # define directions along track and along scan
                T=inverse_haversine((lat,lon), track/2, orbit*pi/180)
                CT=(T[0]-lat,T[1]-lon)
                S=inverse_haversine((lat,lon), scan/2, (orbit+90)*pi/180)
                CS=(S[0]-lat,S[1]-lon)
                # create polygon for footprint       
                mystr='POLYGON(('
                for coefs in [(1,1),(1,-1),(-1,-1),(-1,1),(1,1)]:
                    (ct,cs)=coefs
                    mystr=mystr+str(lon+ct*CT[1]+cs*CS[1])+' '+ str(lat+ct*CT[0]+cs*CS[0])+','
                mystr=mystr+'))'
                mystr=mystr.replace(',)',')')
                mygeometry = QgsGeometry.fromWkt(mystr)
                newfeat=QgsFeature()
                newfeat.setGeometry(mygeometry)
                L=[feat['longitude']]
                L.append(feat['latitude'])
                L.append(feat['scan'])
                L.append(feat['track'])
                L.append(feat[an_frp])
                L.append(feat[an_day_int])
                L.append(feat['acq_time'])
                L.append(feat['instrument'])
                #L.append(feat['ACQ_DATE'])
                newfeat.setAttributes(L)
                res=pr.addFeature(newfeat)
            newlayer.updateExtents() 
            newlayer.setCrs(mylayer.crs())
            return newlayer
        newlayer=create_footprints(mylayer,K)
        ln_new='footprints'
        if K!=1: ln_new='footprints_K'+str(int(K*100))
        ln_diss=ln_new+'_diss'
        newlayer.setName(ln_new)
        myproject.addMapLayer(newlayer)
        # dissolve days and create ln_isocronas_diss to be exported as kml
        #dict_params={'FIELD': [an_day_int,'instrument']}
        #mylayer=my_processing_run("native:dissolve",ln_new,dict_params,ln_diss)
        if INPUT_MODIS:
            dict_params={'EXPRESSION':' "instrument" = \'MODIS\' ','METHOD':0}
            mylayer=my_processing_run("native:extractbyexpression",ln_new,dict_params,'modis_footprints')
        if INPUT_VIIRS:
            dict_params={'EXPRESSION':' "instrument" = \'VIIRS\' ','METHOD':0}
            mylayer=my_processing_run("native:extractbyexpression",ln_new,dict_params,'viirs_footprints')


if PROCESS_ISOCRONAS:
    vlayer=my_add_vector_layer(fn_isocronas,ln_isocronas)
    
    # make copy
    vlayer.selectAll()
    mylayer=my_processing_run("native:saveselectedfeatures",ln_isocronas,{},ln_isocronas_new)
    
    # create new attribute an_day and populate it with the day
    # create new attributes
    pr = mylayer.dataProvider()
    
    myattribs=pr.fields().names()
    
    if an_day_int not in myattribs: 
        L=[QgsField(an_day_int, QVariant.Int)] 
        pr.addAttributes(L)
        mylayer.updateFields()
    
    # delete area field    
    if 'AREA_HA' in myattribs:
        idx=pr.fieldNameIndex('AREA_HA')
        pr.deleteAttributes([idx])
        mylayer.updateFields()
    
    # populate
    with edit(mylayer):
        for f in mylayer.getFeatures():
            # populate an_day
            x=f[an_isocronas]
            f[an_day_int]=dt.strptime(x+'_08_2018', '%d_%H:%M_%m_%Y').day
            res=mylayer.updateFeature(f) # to be silent
    
    # delete an_isocronas field  (not needed anymore) 
    if an_isocronas in myattribs:
        idx=pr.fieldNameIndex(an_isocronas)
        pr.deleteAttributes([idx])
        mylayer.updateFields()
    
    # dissolve days and create ln_isocronas_diss to be exported as kml
    dict_params={'FIELD': [an_day_int]}
    mylayer=my_processing_run("native:dissolve",ln_isocronas_new,dict_params,ln_isocronas_diss)
    

