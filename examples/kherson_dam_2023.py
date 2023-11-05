import rasterio
import numpy as np
import matplotlib.pyplot as plt
import os


fn=r'C:/Users/mlc/Downloads/S2A-long-33-lat-47-B8-2023-6-5-2a.tif' # antes inundação
#fn=r'C:/Users/mlc/Downloads/S2A-long-33-lat-47-B8-2023-6-5-2b.tif' # deslocado para Este
#fn=r'C:/Users/mlc/Downloads/S2A-long-33-lat-47-B8-2023-6-5-2c.tif' # deslocado para Sul (pouca água)

FOLDER=r"C:\Users\mlc\OneDrive - Universidade de Lisboa\Documents\geomatica-sigdr-2020-2021-2022-2023\avaliacoes-frequencias-notas-2020-2023\2022_2023\enunciados\chamada_2"
fn=os.path.join(FOLDER,"dnipro-pre-jun-6.tif")
fn=os.path.join(FOLDER,"dnipro-pos-jun-15.tif")
fn=os.path.join(FOLDER,"dif.tif")


# convert to array with rasterio
with rasterio.open(fn) as src:
    my2Darray = src.read(1) # 1st band
    mycrs=src.crs

N=my2Darray.shape[0]*my2Darray.shape[1]

# Flatten the array
array_flattened = my2Darray.flatten()

array_flattened[np.abs(array_flattened)>N]=0

# Plot the histogram
plt.hist(array_flattened, bins=200)  # Adjust the number of bins as per your requirements
plt.xlabel('Valor do pixel', fontsize=20)
plt.ylabel('Número de pixels' , fontsize=20)
plt.title('Histograma da banda IVP')

#plt.xlim(0, 7000) 
plt.tick_params(axis='both', labelsize=20) 

plt.show()
