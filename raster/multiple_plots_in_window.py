import matplotlib.pyplot as plt

# agri and sap are 2d-arrays

# plot in window
f, axarr = plt.subplots(2,1) 
axarr[0].imshow(agri,cmap='gray_r')
axarr[1].imshow(sap,cmap='gray_r')
plt.show()
