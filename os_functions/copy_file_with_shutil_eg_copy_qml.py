import shutil
import os

# input data: COSsim
cossimname='COSsim_2020_N3_v1_TM06.tif'
fn=os.path.join(folder,cossimname)

# pick extension (study area)
ext=(-61000, -91000, -54000, -86000)

# convert to string
EXT='_'.join([str(abs(x)) for x in ext])

# output file name (of cropped image)
fout=os.path.join(folder,os.path.splitext('COSsim_2020_N3_v1_TM06_crop.tif')[0]+'_'+EXT+'.tif')

# copy qml file if necessary
qmlfile=os.path.join(folder,os.path.splitext(cossimname)[0]+'.qml')
qmlfileout=os.path.splitext(fout)[0]+'.qml'
if os.path.exists(qmlfile) and not os.path.exists(qmlfileout):
    shutil.copy(qmlfile, qmlfileout)
