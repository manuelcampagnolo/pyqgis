

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

# my working folder
myfolder=r'C:\Users\mlc\OneDrive - Universidade de Lisboa\Documents\profissional-isa-cv\agregacao\aula\dados\monchique_2018' # CHANGE
# source auxiliary functions (instead of importing module)
exec(open(os.path.join(myfolder,'auxiliary_functions.py').encode('utf-8')).read())

# main options
CREATE_LAYER_FOOTPRINTS=True
CREATE_LEGEND_MODIS=False
CREATE_LEGEND_VIIRS=False
option_size='brightness'

# my remaining constants
fn_viirs = os.path.join(myfolder,'DL_FIRE_SV-C2_278445','fire_archive_SV-C2_278445.csv')
ln_viirs ='viirs' 
ln_viirs_day='viirs_day'
fn_modis = os.path.join(myfolder,'DL_FIRE_M-C61_278444','fire_archive_M-C61_278444.csv')
ln_modis ='modis' 
ln_modis_day='modis_day'
ln_af='af'
# Attributes
an_frp='frp'
an_track='track'
an_scan='scan'
an_bright='brightness'
# new attributes
an_day="day" # decimal day
an_foot='footprint'
an_frpkm2="frpkm2"
an_size='size' # chose which
# orbits inclinations
orbit_modis=98.2
orbit_viirs=98.79

#clear layer tree and canvas and creates instance of project
myproject,mycanvas = my_clean_project()

######################  read and process csv table with lon, lat coordinates
# parameters to read csv file (some options)
#params='?delimiter=%s&xField=%s&yField=%s' % (",", "Lon", "Lat")
#sep=';'
#params="?delimiter={}&detectTypes=yes&geomType=none".format(sep)
#params="?delimiter=;&detectTypes=yes&geomType=none"
params='?delimiter=%s&xField=%s&yField=%s' % (",", "longitude", "latitude")

# uri for reading the file as "delimitedtext"
uri='file:///'+fn_viirs+params
mylayer = QgsVectorLayer(uri, '', "delimitedtext")
mylayer.setName(ln_viirs)
mylayer.setCrs(QgsCoordinateReferenceSystem(4326))
myproject.addMapLayer(mylayer)

uri='file:///'+fn_modis+params
mylayer = QgsVectorLayer(uri, '', "delimitedtext")
mylayer.setName(ln_modis)
mylayer.setCrs(QgsCoordinateReferenceSystem(4326))
myproject.addMapLayer(mylayer)

# merge viirs and modis
# "native:mergevectorlayers", {'LAYERS':[
dict_params={'LAYERS':[ln_modis,ln_viirs]}
mylayer=my_processing_run("native:mergevectorlayers",'',dict_params,ln_af)

# remove previous layer
my_remove_layer(ln_viirs)
my_remove_layer(ln_modis)

print(mylayer.dataProvider().fields().names())

# creaate new attributes
pr = mylayer.dataProvider()
pr.addAttributes([QgsField(an_day, QVariant.Double), QgsField(an_size,  QVariant.Double),QgsField(an_foot,  QVariant.Double),QgsField(an_frpkm2,  QVariant.Double)])
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
Mx,mn=0,10**8
for f in mylayer.getFeatures():
   if  f[an_bright] > Mx: Mx= f[an_bright]
   if  f[an_bright] < mn: mn= f[an_bright]

# fill "day" attribute
with edit(mylayer):
    for f in mylayer.getFeatures():
        # populate an_day
        h=float(np.floor(f['acq_time']/100))
        m=float(f['acq_time']-100*h)
        #print(h,m)
        #print(float(f['acq_date'].day())+h/24+m/(60*24))
        f[an_day]=float(f['acq_date'].day())+h/24+m/(60*24)
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
if not CREATE_LAYER_FOOTPRINTS: stop

# vlayer in 4326
# track and scan in km, orbit in degrees
def create_footprints(mylayer,K):
    newlayer=QgsVectorLayer("Polygon", "newlayer", "memory")
    pr = newlayer.dataProvider()
    pr.addAttributes([QgsField("longitude", QVariant.Double),QgsField("latitude",  QVariant.Double),QgsField("frp", QVariant.Double)])
    newlayer.updateFields() 
    for feat in mylayer.getFeatures():
        track=K*feat['track']
        scan=K*feat['scan']
        if feat['instrument']=='MODIS': orbit=orbit_modis
        if feat['instrument']=='VIIRS': orbit=orbit_viirs
        f=feat.geometry().asPoint()
        lon,lat=f.x(),f.y() # lon, lat of the feature
        # define directions along track and along scan
        T=inverse_haversine((lat,lon), track/2, (orbit-90)*pi/180)
        CT=(T[0]-lat,T[1]-lon)
        S=inverse_haversine((lat,lon), scan/2, (orbit)*pi/180)
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
        newfeat.setAttributes([feat['longitude'],feat['latitude'],feat['frp']])
        res=pr.addFeature(newfeat)
    newlayer.updateExtents() 
    newlayer.setCrs(mylayer.crs())
    return newlayer

newlayer=create_footprints(mylayer,K=0.5)

myproject.addMapLayer(newlayer)