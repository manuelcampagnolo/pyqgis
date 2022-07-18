import os
# just filename (with extension), with no path:
filename=os.path.basename('/root/dir/sub/file.ext')
# filename (without extension)
print(os.path.splitext(filename)[0])
# extension
print(os.path.splitext(filename)[1])
