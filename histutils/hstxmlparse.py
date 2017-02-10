#!/usr/bin/env python
# this is a pretty laughable approach, but I didn't take the time to figure out Xpath queries from within Python
# I plan to never use XML in the future observing seasons, but rather HDF5 to store/load config data
from subprocess import Popen,PIPE



def sysxpath(cluster,variable,xmlfn):
    syscall =['xpath','-e','/LVData/Cluster/Cluster[Name='+cluster+
              ']/SGL[Name=' + variable + ']/Val','-q',xmlfn,'|','grep','-o','-P',
              '(?<=<Val>).*(?=</Val>)']

    po = Popen(syscall, stdout=PIPE, shell=False)
    so,serr = po.communicate()
    return so