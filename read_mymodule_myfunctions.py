# imports module. But when running still complains NameError: name 'QgsProject' is not defined when calling my_clean_project
# seems that it doesn't accept functions that involve pyqgis built-in functions
import qgis # already loaded
import processing # idem
import os # file management
import sys # to get sys.path

# opção para retirar as layers desnecessárias após serem usadas
REMOVE_LAYERS=True

# adapt
# folder where data and auxiliary functions are:
myfolder=r'C:\Users\mlc\OneDrive - Universidade de Lisboa\Documents\temp'
# add folder to sys.path
sys.path.append(myfolder)
# import my functions
from cascais_COS_OSM_funcoes_auxiliares import my_clean_project,my_processing_run,my_add_vector_layer,my_remove_layer
