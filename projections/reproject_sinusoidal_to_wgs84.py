import pyproj
import string # generate randomm string
import random
from haversine import haversine, Unit, inverse_haversine, Direction

# proj description of MODIS sinusoidal projectio; a,b are compulsory; otherwise the projection is not well positioned
crs_sinu='+proj=sinu +lon_0=0 +x_0=0 +y_0=0 +ellps=WGS84 +datum=WGS84 +units=m +a=6371007.181 +b=6371007.181 +no_defs'

# fn: csv input file with path
# ln: output layer name
# X,Y are the names of the columns with coordinates in fn 
# inputCRSTYPE can be 'proj4' or 'epsg'
# inputCRSTYPE is a string if 'proj4' and an integer if 'epsg'
def create_4326_layer_from_lat_lon_txt_csv(fn,ln,X,Y,inputCRSTYPE,inputCRS,sep=","):
    params='?delimiter=%s&xField=%s&yField=%s' % (sep, X, Y)
    uri='file:///'+fn+params
    mylayer = QgsVectorLayer(uri, '', "delimitedtext")
    #print(mylayer.dataProvider().fields().names())
    #mylayer.dataProvider().capabilitiesString()
    #
    # all this below is to add capabilities to layer: it is now open with ogr, and will have an extra field "fid"
    # SaveVectorOptions contains many settings for the writer process
    save_options = QgsVectorFileWriter.SaveVectorOptions()
    transform_context = QgsProject.instance().transformContext()
    # Write to GeoPackage (default)
    # instead of simply to os.path.splitext(fn)[0]+'.gpkg'
    letters = string.ascii_lowercase
    lixo=(''.join(random.choice(letters) for i in range(10)) )
    error = QgsVectorFileWriter.writeAsVectorFormatV3(mylayer, os.path.join(myfolder,lixo+'.gpkg'),transform_context,save_options)
    mylayer=QgsVectorLayer(os.path.join(myfolder,lixo+'.gpkg'),ln,"ogr") # adds fid column
    # reproject if necessary
    if not inputCRS==4326:
        if inputCRSTYPE=='proj4':
            crs_input = pyproj.CRS.from_proj4(inputCRS)
        elif inputCRSTYPE=='epsg':
            crs_input=CRS.from_epsg(inputCRS)
        else: 
            print('wrong CRSTYPE')
            stop
        # class to perform the coordinate transformation
        transformer = pyproj.Transformer.from_crs(crs_input, "EPSG:4326", always_xy=True)
        with edit(mylayer):
            for f in mylayer.getFeatures():
                (LON,LAT)=transformer.transform(f['X'],f['Y'])
                mystr='POINT('+str(LON)+' ' + str(LAT)+')'
                mygeometry = QgsGeometry.fromWkt(mystr)
                f.setGeometry(mygeometry)
                res=mylayer.updateFeature(f) # to be silent
    mylayer.setCrs(QgsCoordinateReferenceSystem(4326))
    mylayer.setName(ln)
    return mylayer
