# export mylayer as a KML file saving symbology (seems to work for  single symbol but not for categorized)

#mySymbol1 = QgsFillSymbol.createSimple({'color':'#ff0000','color_border': '#000000','width_border': 1})
#myRenderer  = vlayer.renderer()
#myRenderer.setSymbol(mySymbol1)
#mylayer.triggerRepaint()
   
options = QgsVectorFileWriter.SaveVectorOptions()
options.driverName = "KML"
options.symbologyExport = QgsVectorFileWriter.FeatureSymbology
fn=os.path.join(myfolder,'output.kml')
QgsVectorFileWriter.writeAsVectorFormatV3(mylayer, fn_diss, QgsProject.instance().transformContext(), options)
