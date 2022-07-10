# search string in file

import os
import re # regular expressions
import copy # to copy string

# (a|b) matches either 'a' or 'b'
# '.' replace one character
# '.*' replaces any string of characters
# '^abc' means that the string starts with 'abc'
# 'xyz$' means that the string end with 'xyz'
re_string = '(A|a)dd.*(L|l)ayer'
re_string='^def'
re_string="QVariant"

# below, f is the file name (with no path)
for f in os.listdir(myfolder):
    if os.path.isfile(os.path.join(myfolder,f)) and '.py' in f:
        # opening a text file
        myfile = open(os.path.join(myfolder,f), "r")  
        # setting flag and index to 0
        flag = 0
        index = 0 # index for the line in file
        # Loop through the file line by line
        for line in myfile:  
            if flag==1: break # stops searching file after 1st match
            index += 1 
            # checking string is present in line, or not
            if re.search(re_string,line): 
                flag = 1
                firstline=copy.copy(line)
            
        # checking condition for string found or not
        if flag == 1: 
            print(f, '['+re_string+']', 'Found In Line', index)
            print(firstline)
            print(line)
        # closing text file    
        myfile.close()
