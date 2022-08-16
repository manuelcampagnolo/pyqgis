from osgeo import gdal

# ext=(-61000, -91000, -54000, -86000)
# fn and fout: paths to input and output files

# crop with gdal
if not os.path.exists(fout):
    gdal.Warp(destNameOrDestDS = fout, 
              srcDSOrSrcDSTab  = fn,
              outputBounds     = ext,
              cropToCutline    = True,
              copyMetadata     = True)
