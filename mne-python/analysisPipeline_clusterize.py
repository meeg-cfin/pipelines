# -*- coding: utf-8 -*-
"""
Adapted on Aug 2015)
(Orig created on Wed Mar 19 09:34:24 2014)

@orig_author: lau & mads
@author: andreas & niels christian
@author: kousik
"""
# Function to cluterize automatic artefact rejection
# Low-level function - run via wrapper
# Needs rawRoot, resultsRoot, scriptsRoot


''' ANALYSIS PIPELINE '''

import os
import matplotlib
matplotlib.use('TkAgg')
print('TkAgg')
import matplotlib.pyplot as plt


import mne
import numpy as np
from subprocess import check_output     # in order to be able to call the bash command 'find' and use the output
from sys import argv

matplotlib.interactive(True)
plt.close('all')

printStatus = 1
ignoreDepWarnings = 0
if ignoreDepWarnings:
    import warnings
    warnings.filterwarnings("ignore", category=DeprecationWarning)

## which steps to run
## first steps
read = 1 ## can't save filtered files, so don't run this time \
         ## consuming process every time
Filter = 1
saveICA = 1
ICAraw = 1


## set path and subs

#print argv
file_name        = argv[1]
rawRoot          = argv[2]
resultsRoot      = argv[3]
scriptsRoot       = argv[4]
print file_name

## read in functions from 'analysisPipelineFunctions'
execfile(scriptsRoot+'/analysisPipelineFunctions_eog-ecg.py')

os.chdir(rawRoot) ## set series directory
new_name = file_name[0:-4]

''' READ AND FILTER'''
if read:
    print('Reading subject: ' +file_name)
    ## read raws
    raw = readRawList(file_name,preload=True)
if Filter:
    ## filter
    l_freq, h_freq = 1, 100.0
    filterRaw(raw,l_freq,h_freq)


'''INDEPENDENT COMPONENT ANALYSIS (EYE BLINKS)'''
if ICAraw:
    saveRoot = (resultsRoot +  '/')
    ICAList,ICAcomps = runICA(raw,saveRoot,new_name)

'''SAVE'T ALL'''
if saveICA:
    if printStatus:
        print('Saving Files for subject: ' +  new_name)
#                os.chdir(root + allSeries[i] + '/mne') ## set saving directory
    saveRoot = (resultsRoot + '/')
    saveRaw(ICAList,ICAcomps,saveRoot,new_name)
