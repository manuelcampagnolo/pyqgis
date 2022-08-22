import os
import shutil
from osgeo import gdal
import matplotlib.pyplot as plt
import numpy as np
import rasterio
from rasterio.transform import from_bounds #


folder=r'C:\Users\mlc\Downloads'
#myscriptsfolder=r'C:\Users\mlc\OneDrive - Universidade de Lisboa\Documents\Aulas-Cursos\scripts_python'
#exec(open(os.path.join(myscriptsfolder,'auxiliary_functions.py').encode('utf-8')).read())

# input data: COSsim
cossimname='COSsim_2020_N3_v1_TM06.tif'

# pick extension (study area)
ext=(-61000, -91000, -54000, -86000)
ext=(-57000, -90000, -54000, -89000)

################################################################################ funcoes auxiliares

# convolution with numpy
def convolve2D(image, kernel, padding=0, strides=1):  # if y % strides == 0:
    # Cross Correlation
    kernel = np.flipud(np.fliplr(kernel))
    # Gather Shapes of Kernel + Image + Padding
    xKernShape = kernel.shape[0]
    yKernShape = kernel.shape[1]
    xImgShape = image.shape[0]
    yImgShape = image.shape[1]
    # Shape of Output Convolution
    xOutput = int(((xImgShape - xKernShape + 2 * padding) / strides) + 1)
    yOutput = int(((yImgShape - yKernShape + 2 * padding) / strides) + 1)
    output = np.zeros((xOutput, yOutput))
    # Apply Equal Padding to All Sides
    if padding != 0:
        imagePadded = np.zeros((image.shape[0] + padding*2, image.shape[1] + padding*2))
        imagePadded[int(padding):int(-1 * padding), int(padding):int(-1 * padding)] = image
        #print(imagePadded)
    else:
        imagePadded = image
    # Iterate through image
    for y in range(image.shape[1]):
        # Exit Convolution
        if y > image.shape[1] - yKernShape:
            break
        # Only Convolve if y has gone down by the specified Strides
        if y % strides == 0:
            for x in range(image.shape[0]):
                # Go to next row once kernel is out of bounds
                if x > image.shape[0] - xKernShape:
                    break
                try:
                    # Only Convolve if x has moved by the specified Strides
                    if x % strides == 0:
                        output[x, y] = (kernel * imagePadded[x: x + xKernShape, y: y + yKernShape]).sum()
                except:
                    break
    return output



# clear layer tree and canvas
def my_clean_project():
    # project and canvas
    myproject = QgsProject.instance() # does not write to file
    mycanvas = iface.mapCanvas()
    # clear layers in project
    myproject.removeAllMapLayers()
    # refresh canvas
    mycanvas.refreshAllLayers()
    return myproject,mycanvas

def my_add_raster_layer(fn,ln):
    mylayer=QgsRasterLayer(fn,"", "gdal")
    mylayer.setName(ln)
    myproject.addMapLayer(mylayer)
    return mylayer

##########################################################################


# create clean project
myproject,mycanvas = my_clean_project()

fn=os.path.join(folder,cossimname)
my_add_raster_layer(fn,'COSsim')

# convert extension  to string
EXT='_'.join([str(abs(x)) for x in ext])
# file name of cropped image
fout=os.path.join(folder,os.path.splitext('COSsim_2020_N3_v1_TM06_crop.tif')[0]+'_'+EXT+'.tif')
# copy qml file if necessary
qmlfile=os.path.join(folder,os.path.splitext(cossimname)[0]+'.qml')
qmlfileout=os.path.splitext(fout)[0]+'.qml'
if os.path.exists(qmlfile) and not os.path.exists(qmlfileout):
    shutil.copy(qmlfile, qmlfileout)

# crop with gdal to ext
if not os.path.exists(fout):
    gdal.Warp(destNameOrDestDS = fout, 
              srcDSOrSrcDSTab  = fn,
              outputBounds     = ext,
              cropToCutline    = True,
              copyMetadata     = True)

# add cropped layer
my_add_raster_layer(fout,'COSsim_cropped')

# convert to array with rasterio
with rasterio.open(fout) as src:
    cossim = src.read(1)
    mycrs=src.crs

# agricultura
agri=(cossim // 100 ==2).astype(int)
# SAP
sap=np.logical_or(cossim==311, cossim==322).astype(int)

# plot in window agri and sap
f, axarr = plt.subplots(2,1) 
axarr[0].imshow(agri,cmap='gray_r')
axarr[1].imshow(sap,cmap='gray_r')
plt.show()

# build circular kernel
k=11
K=np.full((k,k),1)
rk=(k-1)/2 # radius
# make kernel circular
for x in range(k):
    for y in range(k):
        if (x-rk)**2+(y-rk)**2 > rk**2:
            K[x,y]=0
print(np.sum(K))


Nref=81 # Bruno, kernel circular de diam 11
pmin,pmax=40/Nref,81/Nref

# several plots
#subplot(r,c) provide the no. of rows and columns
f, axarr = plt.subplots(2,2) 

# plotrow, plotcol,k (kernel), iter (#iterations of convolve), pmin, pmax
mydict={0: (0,0,5,7,1,pmin,pmax), 1: (0,1,7,9,1,pmin,pmax), 2: (1,0,5,11,1,pmin,pmax), 3: (1,1,7,11,1,pmin,pmax)}
#mydict={0: (0,0,1,0,pmin,pmax), 1: (0,1,11,1,0.4,0.6), 2: (1,0,11,1,0.3,0.7), 3: (1,1,11,1,0.2,0.8)}

def combine_kernels(fagr,fsap,agri,sap):
    Y=np.logical_and(fsap+fagr>pmin, fsap+fagr<=pmax)
    Y=np.logical_and(Y,fagr>5./Nref)
    Y=np.logical_and(Y, fagr<pmax)
    Y=np.logical_and(Y,fsap>2./Nref)
    Y=np.logical_and(Y,fsap<pmax)
    Y=np.logical_and(Y,agri+sap>0).astype(int)
    return Y

for idx,(i,j,k,k2,iter,pmin,pmax) in mydict.items():
    if k>1:
        K=create_circular_kernel(k)
        rk=int((k-1)/2)
        # apply convolution
        fagr=convolve2D(agri,K,rk)/np.sum(K)
        fsap=convolve2D(sap,K,rk)/np.sum(K)
        # apply conditions (Bruno)
        Y=combine_kernels(fagr,fsap,agri,sap)
        K=create_circular_kernel(k2)
        rk=int((k2-1)/2)
        Y=convolve2D(Y,K,rk)/np.sum(K)
        Y=(Y>0.5).astype(int)
        axarr[i,j].imshow(Y,cmap='viridis')
plt.show()

