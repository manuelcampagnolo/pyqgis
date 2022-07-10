# Unleash QGIS with Python / ISA / ULisboa
# Assignment #2
# May 2022
# Manuel Campagnolo

import qgis # already loaded
import processing # idem
import os # file management
from osgeo import ogr # connection to geopackage

parent=iface.mainWindow() # necessary for QMessageBox

myfolder=r'C:\Users\mlc\OneDrive - Universidade de Lisboa\Documents\Aulas-Cursos\Curso_PyQGIS_2a_edicao\PyQGIS'
# load auxiliary functions
exec(open(os.path.join(myfolder,'scripts','auxiliary_functions.py').encode('utf-8')).read())
exec(open(os.path.join(myfolder,'scripts','auxiliary_functions_assignment2_complete_code.py').encode('utf-8')).read())

# input data
# geopackage vector layers: 'Slopes'; 'SoilType'; 'LandUse'; 'Roads'; 'Streams'
# geopackage tables:'LandUseTypes' ; 'RoadProtection' ; 'SoilProductivity'
fn=os.path.join(myfolder,'input','CascaisZoningAssignment2.gpkg')
# Digital Elevation Model
fn_dem=os.path.join(myfolder,'input','dem_cascais_50m.tif')
ln_dem='DEM'

# constants
val1=10  # maximum slope in percentage for the 1st slope class
val2=20  # maximum slope in percentage for the 2nd slope class
mydict={1:(val1,'up to {}%'.format(val1)),2:(val2,'between {} and {}%'.format(val1,val2))}

# select patches with at least this proportion of forest
minimumForest=0.4

# keys for joins
key_landUse='codeUse'
key_landUseTypes='Code'
key_roadProt='Type'
key_roads='roadType'
key_soilType='COD1'
key_soilProd='code'

# some expressions 
exp_soil=' "Productivt" = \'low\' OR  "Productivt" = \'medium\' ' # table SoilProductivity
exp_slopes = '("COS2018_n1" <> \'5.Florestas\' AND  "SlopeType" = \'up to {}%\' ) OR \
( "COS2018_n1" = \'5.Florestas\' )'.format(val1)
exp_streams = ' "strType" = \'main\' ' # table Streams
exp_area = ' \"area\" >300000 '  
exp_use='"COS2018_n1" =  \'4.Superfícies agroflorestais\' OR \
"COS2018_n1" =  \'5.Florestas\' OR \
"COS2018_Lg" = \'2.3.3.1 Agricultura com espaços naturais e seminaturais\' OR \
"COS2018_Lg" =  \'3.1.2.1 Pastagens espontâneas\' OR \
"COS2018_Lg" =  \'7.1.3.1 Vegetação esparsa\' OR \
"COS2018_n1" =  \'7. Espaços descobertos ou com pouca vegetação\'  '
exp_forest=' "COS2018_n1" =  \'5.Florestas\' '

# attribute in 'RoadProtection' for buffers
property_distance=QgsProperty.fromExpression('"Distance"')

##################################################### project; add layers
# Create project
myproject,mycanvas= my_clean_project()

# create vector layer where features have slopes up to val1 and between val1 and val2, named 'slopesVal'
# mydict defines val1, val2, and the labels for new attribute 'slopeType'
vlayer=create_vector_slope_classes(fn_dem,mydict,'slopeType','slopesToValidate')

# Check and fix layer
mylayer,not_valid_ids=fix_not_valid_features(vlayer,'Slopes')
my_remove_layer('slopesToValidate')

################################################# read Geopackage
# load layers into project with name equal to geopackage layer name
gpkg_layers = [l.GetName() for l in ogr.Open(fn)]
for ln in gpkg_layers:
    my_add_vector_layer(fn + "|layername=" + ln,ln)

################################################# Spatial Analysis
# clip LandUse to Cascais Municipality
dict_params={'OVERLAY':'CascaisLimits'}
mylayer=my_processing_run("native:clip",'LandUse',dict_params,'LandUseCascais')
my_remove_layer('LandUse')
my_remove_layer('CascaisLimits')

# select suitable land use
dict_params={'EXPRESSION': exp_use}
mylayer=my_processing_run("native:extractbyexpression",'LandUseCascais',dict_params,'suitableLandUse')

# select forest
dict_params={'EXPRESSION': exp_forest}
mylayer=my_processing_run("native:extractbyexpression",'LandUseCascais',dict_params,'forestLandUse')
my_remove_layer('LandUseCascais')

# Dissolve forest: to be used at the end
dict_params={}
mylayer=my_processing_run("native:dissolve",'forestLandUse',dict_params,'forestLandUseDissolved')
my_remove_layer('forestLandUse')

# Intersection of suitable Land Use with Slopes  
dict_params={'OVERLAY':'Slopes'}
mylayer=my_processing_run("native:intersection",'suitableLandUse',dict_params,"Use_and_Slopes")
my_remove_layer('Slopes')
my_remove_layer('suitableLandUse')

# Select suitable Slopes and LandUse
dict_params={'EXPRESSION': exp_slopes}
mylayer=my_processing_run("native:extractbyexpression",'Use_and_Slopes',dict_params,'suitable_Use_and_Slopes')
my_remove_layer('Use_and_Slopes')

# join layers about Soil
dict_params={'FIELD': key_soilType,'INPUT_2': 'SoilProductivity', 'FIELD_2':key_soilProd}
mylayer=my_processing_run("native:joinattributestable",'SoilType',dict_params,'soilType_Join')
my_remove_layer('SoilType')
my_remove_layer('SoilProductivity')

# select suitable soil type 
dict_params={'EXPRESSION': exp_soil}
mylayer=my_processing_run("native:extractbyexpression",'soilType_Join',dict_params,'suitableSoilType')
my_remove_layer('soilType_Join')

# clip suitable Land Use and Slope with suitable Soil Type
dict_params={'OVERLAY':'suitableSoilType'}
mylayer=my_processing_run("native:clip",'suitable_Use_and_Slopes',dict_params,'suitable_Use_Type_Slope')
my_remove_layer('suitableSoilType')
my_remove_layer('suitable_Use_and_Slopes')

# join layers about Roads
dict_params={'FIELD': key_roads,'INPUT_2': 'RoadProtection', 'FIELD_2':key_roadProt}
mylayer=my_processing_run("native:joinattributestable",'Roads',dict_params,'roads_Join')
my_remove_layer('RoadProtection')

# Create buffer around Roads
dict_params={'DISTANCE':property_distance,'DISSOLVE':True}
mylayer=my_processing_run("native:buffer",'roads_Join',dict_params,'roadsBuffer')
my_remove_layer('roads_Join')

# Remove roads buffer from suitable areas
dict_params={'OVERLAY':'roadsBuffer'}
mylayer=my_processing_run("native:difference",'suitable_Use_Type_Slope',dict_params,'suitable')
my_remove_layer('roadsBuffer')
my_remove_layer('suitable_Use_Type_Slope')

# Dissolve suitable areas
dict_params={}
mylayer=my_processing_run("native:dissolve",'suitable',dict_params,'suitableDissolvedwithFields')
my_remove_layer('suitable')

# Remove all fields except 'fid' after dissolve
dict_params={'FIELDS':['fid']}
mylayer=my_processing_run("native:retainfields",'suitableDissolvedwithFields',dict_params,'suitableDissolved')
my_remove_layer('suitableDissolvedwithFields')

# Convert to singlepart (spatially connected)
dict_params={}
mylayer=my_processing_run("native:multiparttosingleparts",'suitableDissolved',dict_params,'suitableSinglepart')
my_remove_layer('suitableDissolved')

# Select main streams slopes
dict_params={'EXPRESSION': exp_streams}
mylayer=my_processing_run("native:extractbyexpression",'Streams',dict_params,'mainStreams')
my_remove_layer('Streams')

# Select by location suitable areas that are intersected by main streams
dict_params={'PREDICATE':[0], 'INTERSECT':'mainStreams'}
mylayer=my_processing_run("native:extractbylocation",'suitableSinglepart',dict_params,'suitable_with_mainStreams')
my_remove_layer('suitableSinglepart')

# Calculate areas
dict_params={'CALC_METHOD':2}
mylayer=my_processing_run("qgis:exportaddgeometrycolumns",'suitable_with_mainStreams',dict_params,'suitable_with_area_m2')
my_remove_layer('suitable_with_mainStreams')

# Select  areas with more than a given value (e.g. 300000, in square meters), defined by exp_area
dict_params={'EXPRESSION': exp_area}
mylayer=my_processing_run("native:extractbyexpression",'suitable_with_area_m2',dict_params,'final')
my_remove_layer('suitable_with_area_m2')

# forest
forest=myproject.mapLayersByName('forestLandUseDissolved')[0]

# Select patches with a proportion of forest at least equal to minimumForest
# Create attribute 'propForest'
pr=mylayer.dataProvider()
if 'propForest' not in pr.fields().names(): 
    pr.addAttributes([QgsField('propForest',QVariant.Double)])
    mylayer.updateFields()

# determine list of ids to select + plus fill attribute 'propForest' (optional)
ids=[]
with edit(mylayer):
    for feat in mylayer.getFeatures():
        for featforest in forest.getFeatures():
            areaforest=feat.geometry().intersection(featforest.geometry()).area()
            areapatch=feat.geometry().area()
            if areaforest > minimumForest * areapatch:
                ids.append(feat.id())
            feat['propForest']=areaforest/areapatch
        res=mylayer.updateFeature(feat)

mylayer.select(ids)
