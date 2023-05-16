# Manuel Campagnolo
# ISA/ULisboa 2023
# resolucao_trabalho_geomatica_sigdr_2022_2023
# Projeto Cadastro v2

import qgis # already loaded
import processing # idem
import os # file management
from osgeo import gdal, osr, gdalconst # raster input/output, resampling
import numpy as np
from qgis.PyQt.QtCore import QVariant # types for attributes in vector layers
import re
import shutil
import pickle

turma=3
grupo=4

########################################################### a adaptar:
# NOME DA PASTA E SUBPASTA ONDE ESTÃO OS SCRIPTS
upfolder=r'C:\Users\mlc\OneDrive - Universidade de Lisboa\Documents\geomatica-sigdr-2020-2021-2022-2023\Trabalho_avaliacao\projeto-2022-2023-cadastro-v2\resolucao'
myscriptsfolder= os.path.join(upfolder,'scripts') #r'C:\Users\mlc\Documents\PyQGIS\scripts'
exec(open(os.path.join(myscriptsfolder,'auxiliary_functions.py').encode('utf-8')).read())

# NOME DA PASTA EM QUE ESTÃO OS TRABALHOS DOS GRUPOS
projectsfolder=r'C:\Users\mlc\OneDrive - Universidade de Lisboa\Documents\geomatica-sigdr-2020-2021-2022-2023\Trabalho_avaliacao\Trabalhos_alunos_SIGs\trabalhos_2022_2023'
projectsfolder=r'\\madpet\mlc\Temp' # para discussões

# NOME DA SUBPASTA DO GRUPO 
if turma==0 and grupo==0:
    myfolder=os.path.join(projectsfolder,'Exemplo')

if turma==3 and grupo==4:
    myfolder=os.path.join(projectsfolder,'T3G4','grupo4turma3parte2')

########################################################################
parent=iface.mainWindow() # necessary for QMessageBox

# project and data set CRS
my_crs=3763
# Create project
myproject,mycanvas= my_clean_project()
# set project CRS
myproject.setCrs(QgsCoordinateReferenceSystem(my_crs))

# Ler cdg, atributos e valores para expressões
# indiferente escrever minúsculas ou maiuscúlas pois a função find_files converte com .lower()
# (?!.*PCVAL) to discard PCVAL
# depois de ler a 1a vez, guarda valores lidos em 'my_params.txt'
if 'my_params.txt' not in os.listdir(myfolder):
    L=[]
    Lp=[] # pickle
    # cadastro
    fn_pc,an_ran,exp_ran=find_files(myfolder, r'^Cad.*(shp|gpkg)$',pick_attribute='atrib RAN') 
    L=L+['fn_pc','an_ran','exp_ran']
    Lp=Lp+[fn_pc, an_ran,exp_ran]
    # ren 
    fn_pc,an_ren,exp_ren=find_files(myfolder, r'^Cad.*(shp|gpkg)$',pick_attribute='atrib REN') 
    L=L+['an_ren','exp_ren']
    Lp=Lp+[an_ren,exp_ren]
    # valcadastro dos alunos para comparar
    fn_valcadastro=find_files(myfolder, r'^val.*(shp|gpkg)$') 
    L=L+['fn_valcadastro']
    Lp=Lp+[fn_valcadastro]
    # marcos
    fn_marcos=find_files(myfolder, r'marc.*(shp|gpkg)$')
    L=L+['fn_marcos']
    Lp=Lp+[fn_marcos]
    # PROP
    fn_prop=find_files(myfolder, r'prop.*(txt|csv|gpkg)$') # como é gpkg e txt ou csv vai ler a layer no gpkg
    L=L+['fn_prop']
    Lp=Lp+[fn_prop]
    # CPR
    fn_cpr=find_files(myfolder, r'cpr.*(txt|csv|gpkg)$') # como é gpkg e txt ou csv vai ler a layer no gpkg
    L=L+['fn_cpr']
    Lp=Lp+[fn_cpr]
    # ACESSOS
    fn_rv,an_rv,exp_rv_pavimentadas =find_files(myfolder, r'(^acessos).*(shp|gpkg)$',pick_attribute='tipo e valor pavimentadas (i.e. 2)') 
    L=L+['fn_rv','an_rv','exp_rv_pavimentadas']
    Lp=Lp+[fn_rv,an_rv,exp_rv_pavimentadas]
    fn_rv,an_rv,exp_rv_nao_pavimentadas =find_files(myfolder, r'(^acessos).*(shp|gpkg)$',pick_attribute='tipo e valor nao pavimentadas (i.e. 3)') 
    L=L+['exp_rv_nao_pavimentadas']
    Lp=Lp+[exp_rv_nao_pavimentadas]
    # linhasagua
    fn_la=find_files(myfolder, r'(^linhas).*(shp|gpkg)$') 
    L=L+['fn_la']
    Lp=Lp+[fn_la]
    # corposagua
    fn_ca=find_files(myfolder, r'(^corpos).*(shp|gpkg)$') 
    L=L+['fn_ca']
    Lp=Lp+[fn_ca]
    # CartaSolos
    fn_solos=find_files(myfolder, r'(.*solos).*(shp|gpkg)$') 
    L=L+['fn_solos']
    Lp=Lp+[fn_solos]
    # dem 25 m 3763
    fn_mde=find_files(myfolder, r'^(dem|mde|srtm|alos).*(tif)$') 
    L=L+['fn_mde']
    Lp=Lp+[fn_mde]
    # prec 07 30s 4326
    fn_prec=find_files(myfolder, r'(PREC|wc2).*07.*tif$')
    L=L+['fn_prec']
    Lp=Lp+[fn_prec]
    #fn_pcval=find_files(myfolder, r'^pcval.*(shp|gpkg)$')
    with open(os.path.join(myfolder,'my_params.txt'), 'wb') as f:  
        pickle.dump(Lp, f)
else:
    #print(','.join(L))
    with open(os.path.join(myfolder,'my_params.txt'), 'rb') as f: 
       fn_pc,an_ran,exp_ran,an_ren,exp_ren,fn_valcadastro, fn_marcos,fn_prop,fn_cpr,fn_rv,an_rv,exp_rv_pavimentadas,exp_rv_nao_pavimentadas,fn_la,fn_ca,fn_solos,fn_mde,fn_prec= pickle.load(f)


## output file
fn_prec10m=os.path.join(myfolder,'PREC07_10m.tif')
fn_mde10m=os.path.join(myfolder,'MDE_10m.tif')
ln='input'
ln_out='resampled'

# expressões
exp_fvaa = '(NOT '+exp_ran + ') * \"cosi01_mean\" * min(1, \"prec10m_mean\" /1500) + (' +exp_ran + ') * 0.8'
exp_cv = 'round(($area/10000) * (1 + ( \"ACE0\" + \"REG0\" + \"VAL0_mean\" + \"CON0\" )/4),2)'
an_solos='COD1_solos'


# atributos de PC: será usado num iterador sobre features: não é preciso expressão
#an_ren='ren'

################################################### PARTE 1

# A) lê ficheiro, verifica validade das features, tenta corrigir e devolve layer corrigida
pc=ckeck_and_fix_load_vlayer_validity(fn_pc,'PC')
check_overlaps(pc)
check_gaps_within_hull(pc)

# B) Verificar se os marcos estão sobre os limites das parcelas
# a) extrair linhas de PC
dict_params={}
pc_lines=my_processing_run("native:polygonstolines",pc,dict_params,'pc_lines')
pc_diss=my_processing_run("native:dissolve",pc_lines,dict_params,'pc_diss')

# b) verificar se todos os marcos intersectam com linhas
marcos=my_add_vector_layer(fn_marcos,'marcos')
ids=[]
for featpcline in pc_diss.getFeatures():
    for feat in marcos.getFeatures():
        if not feat.geometry().intersects(featpcline.geometry()):
            ids.append(feat.id())

marcos.select(ids)

# c) mensagem caso haja marcos fora das linhas
if len(ids)>0:
    res=QMessageBox.question(parent,'Marcos mal colocados', str(len(ids))+' marcos mal colocados . Continuar?' )
    if res==QMessageBox.No: stop
else:
    my_remove_layer('pc_diss')
    my_remove_layer('pc_lines')

res=QMessageBox.question(parent,'Fim Parte 1', 'Continuar?' )
if res==QMessageBox.No: stop

# Create project
myproject,mycanvas= my_clean_project()

#my_remove_layer('PC')
#my_remove_layer('marcos')
#my_remove_layer('diss')
#my_remove_layer('overlaps')
mycanvas.refreshAllLayers()

########################################################## PARTE 2

# obter mde10m e prec10m
# resample fn_new to fn_out using fn_ref as the new grid

layer = QgsVectorLayer(fn_rv, "Vector Layer", "ogr")
layer_extent = layer.dataProvider().extent()    
# Extract the extent values
xmin = layer_extent.xMinimum()
ymin = layer_extent.yMinimum()
xmax = layer_extent.xMaximum()
ymax = layer_extent.yMaximum()
exp_extent=str(xmin)+','+str(xmax)+','+str(ymin)+','+str(ymax) + ' [EPSG:3763]'
# '-107746.064900000,-105261.061100000,-86021.605900000,-84116.070800000 [EPSG:3763]'

mydict={'EXTENT': exp_extent,
'TARGET_CRS':QgsCoordinateReferenceSystem('EPSG:3763'),
'PIXEL_SIZE':10,
'NUMBER':1,
'OUTPUT_TYPE':5}
fn_ref=my_processing_run("native:createconstantrasterlayer",'',mydict,'fn_ref')

# nota: não funciona se o ficheiro de output estiver aberto
resample_raster_fn_to_fnout_using_fnref(fn_mde,fn_ref.source(),fn_mde10m,nbands=1,crit='lanczos')
resample_raster_fn_to_fnout_using_fnref(fn_prec,fn_ref.source(),fn_prec10m,nbands=1,crit='bilinear')

my_remove_layer('fn_ref')

# add layer to project
prec10m=my_add_raster_layer(fn_prec10m,'prec10m')
mde10m=my_add_raster_layer(fn_mde10m,'mde10m')
pc=ckeck_and_fix_load_vlayer_validity(fn_pc,'PC')
#pc=my_add_vector_layer(fn_pc,'PC')

###################################################################################

my_add_vector_layer(fn_rv,'RV')

# copy PC to PCVAL
pc.selectAll()
pcval=my_processing_run("native:saveselectedfeatures",'PC',{},'pcval')
my_remove_layer('PC')

# criar layer de estradas pavimentadas EP
dict_params={'EXPRESSION': exp_rv_pavimentadas}
ep=my_processing_run("native:extractbyexpression",'RV',dict_params,'EP')

# criar layer de estradas não pavimentadas ENP
dict_params={'EXPRESSION': exp_rv_nao_pavimentadas}
enp=my_processing_run("native:extractbyexpression",'RV',dict_params,'ENP')
my_remove_layer('RV')

# Create buffers around Roads
dict_params={'DISTANCE':50,'DISSOLVE':True}
ep50=my_processing_run("native:buffer",'EP',dict_params,'EP50')

# Create buffers around Roads
dict_params={'DISTANCE':50,'DISSOLVE':True}
enp50=my_processing_run("native:buffer",'ENP',dict_params,'ENP50')

# NOTA: "with edit" not necessary
pcval.dataProvider().addAttributes([QgsField('ACE0', QVariant.Double)])
pcval.updateFields()

# select by location
with edit(pcval):
    for featpc in pcval.getFeatures():
        featpc['ACE0'] = 0
        res=pcval.updateFeature(featpc)
        #print(featpc.id())
        for featep in enp50.getFeatures():
            #print(featep.id())
            if featpc.geometry().intersects(featep.geometry()):
                featpc['ACE0']=0.5
                res=pcval.updateFeature(featpc)
        for featep in ep50.getFeatures():
            #print(featep.id())
            if featpc.geometry().intersects(featep.geometry()):
                featpc['ACE0']=1.0
                res=pcval.updateFeature(featpc)

res=QMessageBox.question(parent,'ACE', 'Continuar?' )
if res==QMessageBox.No: stop

# remover layer de estradas
my_remove_layer('EP50')
my_remove_layer('ENP50')
my_remove_layer('EP')
my_remove_layer('ENP')
mycanvas.refresh()

######################################################################### REG
# criar atributo 'REG'

ca=my_add_vector_layer(fn_ca,'CA')
la=my_add_vector_layer(fn_la,'LA')

pcval.dataProvider().addAttributes([QgsField('REG0', QVariant.Double)])
pcval.updateFields()
# fill new field  with constant: cycle over features
with edit(pcval):  # necessary to edit layer
    for feat in pcval.getFeatures():
        feat['REG0'] = 0
        res=pcval.updateFeature(feat)
        for featpa in la.getFeatures():
            if feat.geometry().intersects(featpa.geometry()):
                feat['REG0']=1.0
                res=pcval.updateFeature(feat)
        for featpa in ca.getFeatures():
            if feat.geometry().intersects(featpa.geometry()):
                feat['REG0']=1.0
                res=pcval.updateFeature(feat)

res=QMessageBox.question(parent,'REG', 'Continuar?' )
if res==QMessageBox.No: stop

my_remove_layer('LA')
my_remove_layer('CA')



######################################################################### CON
# criar atributo 'CON' 
pcval.dataProvider().addAttributes([QgsField('CON0', QVariant.Double)])
pcval.updateFields()
# fill new field  with constant: cycle over features
with edit(pcval):  # necessary to edit layer
    for feat in pcval.getFeatures():
        if feat[an_ren]==1:
            feat['CON0'] = 0.5
        else:
            feat['CON0'] = 1
        res=pcval.updateFeature(feat)

res=QMessageBox.question(parent,'CON', 'Continuar?' )
if res==QMessageBox.No: stop

########################################################################## VAL
# criar atributo VAL

# A) converter RAN para raster

pcval.dataProvider().addAttributes([QgsField('to_burn', QVariant.Double)])
pcval.updateFields()
with edit(pcval):  # necessary to edit layer
    for feat in pcval.getFeatures():
        #print(feat[an_ran])
        if feat[an_ran]==NULL:
            feat[an_ran]='0' # why string??
        feat['to_burn']=float(feat[an_ran])
        if feat[an_ren]==NULL:
            feat[an_ren]='0' # why string??
        res=pcval.updateFeature(feat)

mydict={'FIELD':'to_burn',
'BURN':None,
'USE_Z':False,
'UNITS':1,
'WIDTH':10,
'HEIGHT':10,
'EXTENT': exp_extent,
'NODATA':-1,
'DATA_TYPE':5,
'INIT':0}
my_processing_run("gdal:rasterize",'pcval',mydict,'ran')

# B) determinar atributo Q de pcval

solos=my_add_vector_layer(fn_solos,'solos')
# select by location
mydict={'PREDICATE':[0],
'INTERSECT':'pcval'}
solos_=my_processing_run("native:extractbylocation",'solos',mydict,'solos_')
my_remove_layer('solos')

# Get the list of attribute fields
attribute_fields = solos_.fields()
# Iterate over the fields and print their names
L=[]
for field in attribute_fields:
    L=L+[field.name()]

if 'Q' not in L: 
    solos_.dataProvider().addAttributes([QgsField('Q', QVariant.Double)])


with edit(solos_):
    for feat in solos_.getFeatures():
        pattern1 = r'^(Ar|AS).*'  
        pattern2= r'^(A|Ba|Bc|Bp|Cb|Sb).*'
        #print(feat[an_solos])
        if not re.match(pattern1,feat[an_solos]) and re.match(pattern2,feat[an_solos]):
            #print('match')
            feat['Q']=1.0
        else:
            #print('no match')
            feat['Q']=0.6
        res=solos_.updateFeature(feat)

# rasterize Q
mydict={'FIELD':'Q',
'BURN':None,
'USE_Z':False,
'UNITS':1,
'WIDTH':10,
'HEIGHT':10,
'EXTENT': exp_extent,
'NODATA':-1,
'DATA_TYPE':5,
'INIT':0}
my_processing_run("gdal:rasterize",'solos_',mydict,'Q')

my_remove_layer('solos_')

# process Q and ran
dict_params={'INPUT_A': 'ran','BAND_A':1, 'INPUT_B': 'Q','BAND_B':1,'FORMULA':'(A==1)*1+(A!=1)*B','NO_DATA':None,'RTYPE':5}
valsolo=my_processing_run("gdal:rastercalculator",'',dict_params,'valsolo')

res=QMessageBox.question(parent,'VALsolos', 'Continuar?' )
if res==QMessageBox.No: stop

my_remove_layer('ran')
my_remove_layer('Q')

# 5b) declives
declive=my_processing_run("native:slope",mde10m,{},'declive')
# valdeclive
mydict={'EXPRESSION':'("declive@1"<2)+ ("declive@1">2)*(1-"declive@1"/90)',
'LAYERS': ['declive'],
'CELLSIZE':0,'EXTENT':None,'CRS':None}
valdeclive=my_processing_run("qgis:rastercalculator",'',mydict,'valdeclive')
my_remove_layer('declive')

# 5c)
mydict={'EXPRESSION':'("prec10m@1">5)+ ("prec10m@1"<=5)*0.6',
'LAYERS': ['prec10m'],
'CELLSIZE':0,'EXTENT':None,'CRS':None}
valprec=my_processing_run("qgis:rastercalculator",'',mydict,'valprec')
my_remove_layer('prec10m')

mydict={'EXPRESSION':'"valsolo@1" * "valdeclive@1" * "valprec@1" ',
'LAYERS': ['valsolo','valdeclive','valprec'],
'CELLSIZE':0,'EXTENT':None,'CRS':None}
val=my_processing_run("qgis:rastercalculator",'',mydict,'val')

my_remove_layer('valsolo')
my_remove_layer('valdeclive')
my_remove_layer('valprec')

# zonal statistics
dict_params={'INPUT_RASTER':'val','RASTER_BAND':1,'COLUMN_PREFIX':'VAL0_','STATISTICS':[2]}
pcval_=my_processing_run("native:zonalstatisticsfb",pcval,dict_params,'pcval_')

res=QMessageBox.question(parent,'VAL', 'Continuar?' )
if res==QMessageBox.No: stop

my_remove_layer('pcval')
my_remove_layer('val')

# Determinar CV
dict_params={'FIELD_NAME':'CV0','FIELD_TYPE':0,'FORMULA': exp_cv,'FIELD_LENGTH':0,'FIELD_PRECISION':0}
pcval=my_processing_run("native:fieldcalculator",pcval_,dict_params,'valcadastro')
my_remove_layer('pcval_')

# Etiquetas para "CV"
layer_settings  = QgsPalLayerSettings()
layer_settings.fieldName = "CV0"
layer_settings.placement = 0
text_format = QgsTextFormat()
text_format.setFont(QFont("Arial", 12))
text_format.setSize(12)
buffer_settings = QgsTextBufferSettings()
buffer_settings.setEnabled(True)
buffer_settings.setSize(1)
buffer_settings.setColor(QColor("white"))
text_format.setBuffer(buffer_settings)
layer_settings.setFormat(text_format)
my_layer_settings = QgsVectorLayerSimpleLabeling(layer_settings)
pcval.setLabelsEnabled(True)
pcval.setLabeling(my_layer_settings)
pcval.triggerRepaint()

# legenda
vals=[]
for feat in pcval.getFeatures():
    vals.append(feat['VAL0_mean'])

mydict=create_sturges_graduated_legend_dict(vals,'viridis',myopacity=0.9,minN=5,decimals=3,minVal=min(vals),units='(VAL)')
create_graduated_legend(pcval,'VAL0_mean',mydict)
