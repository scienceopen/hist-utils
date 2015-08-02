"""
This acts like bash cp --parents in Python
inspiration from
http://stackoverflow.com/questions/15329223/copy-a-file-into-a-directory-with-its-original-leading-directories-appended
"""
from os.path import dirname,join,expanduser,abspath
from os import makedirs
from shutil import copy2
from six import string_types

def cp_parents(files,target_dir):
#%% make list if it's a string
    if isinstance(files,string_types):
        files = [files]
#%% cleanup user
    files = map(expanduser,files)  #relative path or absolute path is fine
    target_dir = abspath(expanduser(target_dir))
#%%
    for f in files:
        try:
            makedirs(join(target_dir, dirname(f).split(target_dir)[-1]))
        except OSError:
            pass
        dest = join(target_dir, f.split(target_dir)[-1])
        #print("Copying {} to {}".format(f, dest))
        copy2(f, dest)