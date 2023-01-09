#resolucao_parte2_trabalho_geomatica_2021_2022.py

import qgis # already loaded
import processing # idem
import os # file management
from osgeo import gdal, osr, gdalconst # raster input/output, resampling
import numpy as np
from qgis.PyQt.QtCore import QVariant # types for attributes in vector layers
import re
import shutil
import pickle # load and dump variables

turma=3
grupo=5

########################################################### a adaptar:
# NOME DA PASTA ONDE ESTÃO OS SCRIPTS
upfolder=r'C:\Users\mlc\OneDrive - Universidade de Lisboa\Documents\geomatica-sigdr-2020-2021-2022\Trabalho_avaliacao\projecto-2021-2022-cadastro'
myscriptsfolder= os.path.join(upfolder,'scripts','good_scripts') #r'C:\Users\mlc\Documents\PyQGIS\scripts'
exec(open(os.path.join(myscriptsfolder,'auxiliary_functions.py').encode('utf-8')).read())

# NOME DA PASTA EM QUE ESTÃO OS TRABALHOS DOS GRUPOS
projectsfolder=r'\\madpet.isa.utl.loc\mlc\Aulas\geomatica-administrativo\geom2122_MC_coord\trabalhos_entregues\parte_2'
projectsfolder=r'C:\Users\mlc\OneDrive - Universidade de Lisboa\Documents\geomatica-sigdr-2020-2021-2022\Trabalho_avaliacao\projecto-2021-2022-cadastro\trabalhos_entregues\parte_2'

# NOME DA SUBPASTA DO GRUPO 
if turma==2 and grupo==1:
    myfolder=os.path.join(projectsfolder,'Trabalho_Turma2_Grupo1')

if turma==2 and grupo==2:
    myfolder=os.path.join(projectsfolder,'turno2_grupo2_parte1-2')

if turma==2 and grupo==3:
    myfolder=os.path.join(projectsfolder,'T2G3')

if turma==2 and grupo==4:
    myfolder=os.path.join(projectsfolder,'T2G4_Turno2Grupo4_parte 2')

if turma==2 and grupo==5:
    myfolder=os.path.join(projectsfolder,'turno2grupo5parte2')

if turma==2 and grupo==6:
    myfolder=os.path.join(projectsfolder,'T2G6_trabalho qgis_t2g6')

if turma==2 and grupo==7:
    myfolder=os.path.join(projectsfolder,'T2G7_Turno2GRupo7Final2')

if turma==3 and grupo==1:
    myfolder=os.path.join(projectsfolder,'T3G1_turma3grupo1parte2')

if turma==3 and grupo==2:
    myfolder=os.path.join(projectsfolder,'T3G2_Trabalho SIG - Turma 3, Grupo 2')

if turma==3 and grupo==3:
    myfolder=os.path.join(projectsfolder,'T3G3_turno3_grupo3_parte2')

if turma==3 and grupo==4:
    myfolder=os.path.join(projectsfolder,'T3G4_entregue25maio')

if turma==3 and grupo==5:
    myfolder=os.path.join(projectsfolder,'T3G5_turno3grupo5parte2_entregue24maio')

if turma==3 and grupo==6:
    myfolder=os.path.join(projectsfolder,'T3G6_turma3grupo6')

if turma==3 and grupo==7:
    myfolder=os.path.join(projectsfolder,'T3G7_turno3_grupo7_entregue_25maio')

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
    fn_pc,an_ran,exp_ran=find_files(myfolder, r'^(?!.*PCVAL)PC.*(shp|gpkg)$',pick_attribute='atrib RAN') 
    fn_pc,an_ren,exp_ren=find_files(myfolder, r'^(?!.*PCVAL)PC.*(shp|gpkg)$',pick_attribute='atrib REN') 
    fn_marcos=find_files(myfolder, r'marc.*(shp|gpkg)$') 
    fn_prop=find_files(myfolder, r'prop.*(txt|csv|gpkg)$') # como é gpkg e txt ou csv vai ler a layer no gpkg
    fn_rv,an_rv,exp_rv_pavimentadas =find_files(myfolder, r'(^rv|estradas).*(shp|gpkg)$',pick_attribute='atrib pavimentação') 
    fn_pa=find_files(myfolder, r'(^pa|gua).*(shp|gpkg)$') 
    fn_cossim=find_files(myfolder, r'^cossim.*(tif)$') 
    fn_mde=find_files(myfolder, r'^(dem|mde|srtm|alos).*(tif)$') 
    fn_prec=find_files(myfolder, r'prec.*(tif)$')
    #fn_pcval=find_files(myfolder, r'^pcval.*(shp|gpkg)$')
    with open(os.path.join(myfolder,'my_params.txt'), 'wb') as f:  
        pickle.dump([fn_pc,an_ran,exp_ran,an_ren,exp_ren,fn_marcos,fn_prop,fn_rv,an_rv,exp_rv_pavimentadas,fn_pa,fn_cossim,fn_mde,fn_prec], f)
else:
    with open(os.path.join(myfolder,'my_params.txt'), 'rb') as f: 
       fn_pc,an_ran,exp_ran,an_ren,exp_ren,fn_marcos,fn_prop,fn_rv,an_rv,exp_rv_pavimentadas,fn_pa,fn_cossim,fn_mde,fn_prec= pickle.load(f)

## my constants
## input files
#fn_pc=os.path.join(myfolder,'PC.gpkg')
#fn_pa=os.path.join(myfolder,'PA.gpkg')
#fn_marcos=os.path.join(myfolder,'Marcos.gpkg')
#fn_rv=os.path.join(myfolder,'RV.gpkg')
#fn_prop=os.path.join(myfolder,'PROP.csv')
#fn_prec=os.path.join(myfolder,'PREC.tif')
#fn_mde=os.path.join(myfolder,'dem_aw3d_pt_25m.tif')
#fn_ref=os.path.join(myfolder,'COSsim_2020_N3_v1_TM06_366.tif') # epsg:3763

## output file
fn_prec10m=os.path.join(myfolder,'PREC10m.tif')
fn_mde10m=os.path.join(myfolder,'MDE10m.tif')
ln='input'
ln_out='resampled'

# expressões
#exp_rv_pavimentadas=' "estado"=\'pavimento\' '
#exp_fvaa = ' (\"ran\" =0) * \"cosi01_mean\" * min(1, \"prec10m_mean\" /1500) + ( \"ran\" =1) * 0.8'
#exp_fvaa = ' (\"'+an_ran+'\" =0) * \"cosi01_mean\" * min(1, \"prec10m_mean\" /1500) + ( \"'+an_ran+'\" =1) * 0.8'
exp_fvaa = '(NOT '+exp_ran + ') * \"cosi01_mean\" * min(1, \"prec10m_mean\" /1500) + (' +exp_ran + ') * 0.8'
exp_cv = 'round(($area/10000) * max(0,(1 + ( \"FACF\" + \"FREG\" + \"FREN\" + \"FVAA\" )/4)),2)'

# atributos de PC: será usado num iterador sobre features: não é preciso expressão
#an_ren='ren'

################################################### PARTE 1

# lê ficheiro, verifica validade das features, tenta corrigir e devolve layer corrigida
pc=ckeck_and_fix_load_vlayer_validity(fn_pc,'PC')
check_overlaps(pc)
check_gaps_within_hull(pc)

# Verificar se os marcos estão sobre os limites das parcelas
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

QMessageBox.information(parent,'Info','Fim da Parte 1')

my_remove_layer('PC')
my_remove_layer('marcos')
mycanvas.refreshAllLayers()

########################################################## PARTE 2

# obter mdePLC e COSsimPLC
# buffer PLC
#dict_params={'DISTANCE':1000,'DISSOLVE':True}
#bufPLC=my_processing_run("native:buffer",'PC',dict_params,'bufPLC')
#my_remove_layer('PC')
## fn_ref
#cossim=my_add_raster_layer(fn_cossim,'cossim')
#

# obter mde10m e prec10m
# resample fn_new to fn_out using fn_cossim as the new grid
resample_raster_fn_to_fnout_using_fnref(fn_mde,fn_cossim,fn_mde10m,nbands=1,crit='lanczos')
resample_raster_fn_to_fnout_using_fnref(fn_prec,fn_cossim,fn_prec10m,nbands=1,crit='bilinear')

# add layer to project
prec10m=my_add_raster_layer(fn_prec10m,'prec10m')
mde10m=my_add_raster_layer(fn_mde10m,'mde10m')
pc=ckeck_and_fix_load_vlayer_validity(fn_pc,'PC')
#pc=my_add_vector_layer(fn_pc,'PC')

###################################################################################FACF
# sequência de seleções de features de PC com EP, EP250m e EP1000m. Em cada passo, 
# seleção por localização, seguida de edição de tabela e limpeza de seleção

my_add_vector_layer(fn_rv,'RV')

# copy PC to PCVAL
pc.selectAll()
pcval=my_processing_run("native:saveselectedfeatures",'PC',{},'pcval')
my_remove_layer('PC')

# criar layer de estradas pavimentadas EP
dict_params={'EXPRESSION': exp_rv_pavimentadas}
ep=my_processing_run("native:extractbyexpression",'RV',dict_params,'EP')
my_remove_layer('RV')

# Create buffers around Roads
dict_params={'DISTANCE':10,'DISSOLVE':True}
ep10=my_processing_run("native:buffer",'EP',dict_params,'EP10m')

dict_params={'DISTANCE':250,'DISSOLVE':True}
ep250=my_processing_run("native:buffer",'EP',dict_params,'EP250m')

dict_params={'DISTANCE':1000,'DISSOLVE':True}
ep1000=my_processing_run("native:buffer",'EP',dict_params,'EP1000m')

# criar atributo 'FACF'
# NOTA: "with edit" not necessary
pcval.dataProvider().addAttributes([QgsField('FACF', QVariant.Double)])
pcval.updateFields()

# select by location
with edit(pcval):
    for featpc in pcval.getFeatures():
        featpc['FACF'] = -0.5
        res=pcval.updateFeature(featpc)
        #print(featpc.id())
        for featep in ep1000.getFeatures():
            #print(featep.id())
            if featpc.geometry().intersects(featep.geometry()):
                featpc['FACF']=0.
                res=pcval.updateFeature(featpc)
        for featep in ep250.getFeatures():
            #print(featep.id())
            if featpc.geometry().intersects(featep.geometry()):
                featpc['FACF']=0.5
                res=pcval.updateFeature(featpc)
        for featep in ep10.getFeatures():
            #print(featep.id())
            if featpc.geometry().intersects(featep.geometry()):
                featpc['FACF']=1.
                res=pcval.updateFeature(featpc)

# remover layer de estradas
my_remove_layer('EP')
my_remove_layer('EP10m')
my_remove_layer('EP250m')
my_remove_layer('EP1000m')
mycanvas.refresh()

######################################################################### FREG
# criar atributo 'FREG'

pa=my_add_vector_layer(fn_pa,'PA')

pcval.dataProvider().addAttributes([QgsField('FREG', QVariant.Double)])
pcval.updateFields()
# fill new field  with constant: cycle over features
with edit(pcval):  # necessary to edit layer
    for feat in pcval.getFeatures():
        feat['FREG'] = 0
        res=pcval.updateFeature(feat)
        for featpa in pa.getFeatures():
            if feat.geometry().intersects(featpa.geometry()):
                feat['FREG']=1.0
                res=pcval.updateFeature(feat)

my_remove_layer('PA')

######################################################################### FREG
# criar atributo 'FREN' 
pcval.dataProvider().addAttributes([QgsField('FREN', QVariant.Double)])
pcval.updateFields()
# fill new field  with constant: cycle over features
with edit(pcval):  # necessary to edit layer
    for feat in pcval.getFeatures():
        if feat[an_ren]==1:
            feat['FREN'] = -0.5
        else:
            feat['FREN'] = 0.
        res=pcval.updateFeature(feat)

##########################################################################
# criar atributo FVAA 
# determinar cos_i
dict_params={'Z_FACTOR':1,'AZIMUTH':180,'V_ANGLE':16}
cos_i=my_processing_run("native:hillshade",mde10m,dict_params,'cos_i')
dict_params={'INPUT_A': cos_i,'BAND_A':1,'FORMULA':'A/255','NO_DATA':None,'RTYPE':5}
# divide by 255
cos_i_01=my_processing_run("gdal:rastercalculator",'',dict_params,'cos_i_01')
my_remove_layer('cos_i')

# determinar cos_i médio por prédio
dict_params={'INPUT_RASTER':'cos_i_01','RASTER_BAND':1,'COLUMN_PREFIX':'cosi01_','STATISTICS':[2]}
pcval_cosi=my_processing_run("native:zonalstatisticsfb",pcval,dict_params,'pcval_cosi')
my_remove_layer('pcval')
my_remove_layer('cos_i_01')

# determinar prec médio por prédio
dict_params={'INPUT_RASTER':'prec10m','RASTER_BAND':1,'COLUMN_PREFIX':'prec10m_','STATISTICS':[2]}
pcval_cosi_prec=my_processing_run("native:zonalstatisticsfb",pcval_cosi,dict_params,'pcval_cosi_prec')
my_remove_layer('pcval_cosi')

# determinar FVAA
dict_params={'FIELD_NAME':'FVAA','FIELD_TYPE':0,'FORMULA': exp_fvaa,'FIELD_LENGTH':0,'FIELD_PRECISION':0}
pcval_fvaa=my_processing_run("native:fieldcalculator",pcval_cosi_prec,dict_params,'pcval_fvaa')
my_remove_layer('pcval_cosi_prec')

# Determinar CV
dict_params={'FIELD_NAME':'CV','FIELD_TYPE':0,'FORMULA': exp_cv,'FIELD_LENGTH':0,'FIELD_PRECISION':0}
pcval=my_processing_run("native:fieldcalculator",pcval_fvaa,dict_params,'PCVAL')
my_remove_layer('pcval_fvaa')

# Etiquetas para "CV"
layer_settings  = QgsPalLayerSettings()
layer_settings.fieldName = "CV"
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
    vals.append(feat['FVAA'])

mydict=create_sturges_graduated_legend_dict(vals,'viridis',myopacity=0.9,minN=5,decimals=3,minVal=min(vals),units='(FVAA)')
create_graduated_legend(pcval,'FVAA',mydict)
