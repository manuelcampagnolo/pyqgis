##################################################################################### dissolve with fixed distance
dict_params={'DISSOLVE' : True, 'DISTANCE' : dist_buf}
mylayer=my_processing_run("native:buffer",ln_isocronas,dict_params,ln_isocronas_buf)
my_remove_layer(ln_isocronas)

# multiple attributes
dict_params={'FIELD': [an_day_int,'instrument']}
mylayer=my_processing_run("native:dissolve",ln_new,dict_params,ln_diss)

##################################################################################### dissolve with attribute distance
property_distance=QgsProperty.fromExpression('"Distance"')
# Create buffer around Roads
dict_params={'DISTANCE':property_distance,'DISSOLVE':True}
mylayer=my_processing_run("native:buffer",'roads_Join',dict_params,'roadsBuffer')
my_remove_layer('roads_Join')
#####################################################################################
