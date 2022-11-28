with edit(mylayer):
        for f in mylayer.getFeatures():
            f[myattrib]=mydict[f['DN']][1]
            res=mylayer.updateFeature(f) # 'res=' to be silent
    return mylayer
