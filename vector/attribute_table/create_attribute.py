# Create attribute 'propForest'
pr=mylayer.dataProvider()
if 'propForest' not in pr.fields().names(): 
    pr.addAttributes([QgsField('propForest',QVariant.Double)])
    mylayer.updateFields()
