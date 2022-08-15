import numpy as np
import rasterio
from rasterio.transform import from_bounds #

# extension of raster with path fout
ext=(-60000, -91000, -54000, -88000)

# convert to array with rasterio
with rasterio.open(fout) as src:
    cossim = src.read(1)
    mycrs=src.crs

# transform: to convert array into Geotiff
W=cossim.shape[1]
H=cossim.shape[0]
transform=rasterio.transform.from_bounds(west=ext[0], south=ext[1], east=ext[2], north=ext[3], width=W, height=H)

# agricultura
agri=(cossim // 100 ==2).astype(int)

# write from array to geotiff (file path=fagri) with rasterio
with rasterio.open(fagri, 'w', driver='GTiff',
                            height = H, width = W,
                            count=1, dtype=rasterio.uint8,
                            crs=mycrs.to_wkt(),
                            transform=transform) as new_dataset:
    new_dataset.write(agri, 1)
