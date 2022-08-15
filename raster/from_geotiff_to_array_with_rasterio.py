fn=path/to/file.tif

# convert to array with rasterio
with rasterio.open(fn) as src:
    my2Darray = src.read(1) # 1st band
    mycrs=src.crs
