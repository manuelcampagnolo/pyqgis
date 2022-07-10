from haversine import haversine, Unit, inverse_haversine, Direction

# determine lat/long from a point, in a certain direction, for a certain distance in km 


# mylayer is a MultiPoint layer (easy to adapt if it is a Point layer)
newlayer=QgsVectorLayer("Polygon", "newlayer", "memory")
pr = newlayer.dataProvider()
# add new attribute to the new layer
pr.addAttributes([QgsField(new_attribute_name,  QVariant.Int)])
newlayer.updateFields()
# create the new features and add them to newlayer
for feat in mylayer.getFeatures():
    # extract point coordinates
    [f]=feat.geometry().asMultiPoint() # for some reason, f is multipoint
    lon,lat=f.x(),f.y() # lon, lat of the feature
    # define Polygon coordinates
    ################################################################### change at will - this uses haversine
    # define directions along track and along scan 
    T=inverse_haversine((lat,lon), reskm/2, 0)
    CT=(T[0]-lat,T[1]-lon)
    S=inverse_haversine((lat,lon), reskm/2, 90*pi/180)
    CS=(S[0]-lat,S[1]-lon)
    # create WKT string that defines the regular polygon 
    mystr='POLYGON(('
    for coefs in [(1,1),(1,-1),(-1,-1),(-1,1),(1,1)]:
        (ct,cs)=coefs
        mystr=mystr+str(lon+ct*CT[1]+cs*CS[1])+' '+ str(lat+ct*CT[0]+cs*CS[0])+','
    mystr=mystr+'))'
    mystr=mystr.replace(',)',')')
    ##################################################################
    # create geometry from WKT string
    mygeometry = QgsGeometry.fromWkt(mystr)
    newfeat=QgsFeature()
    newfeat.setGeometry(mygeometry)
    # compute attribute value
    newfeat.setAttributes([some function of feat[old_attribute_name]])
    # add new feature to the new layer
    res=pr.addFeature(newfeat)
newlayer.updateExtents() 
newlayer.setCrs(mylayer.crs())
