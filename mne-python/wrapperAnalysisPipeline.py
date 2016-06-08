# -*- coding: utf-8 -*-
"""
Created on Thu Feb 18 11:34:25 2016

@author: kousik
"""

"""
Doc string here.
@author mje
@email: mads [] cnru.dk
"""
import os
import sys
import subprocess
import socket
import numpy

cmd = "/usr/local/common/meeg-cfin/configurations/bin/submit_to_isis"

# SETUP PATHS AND PREPARE RAW DATA
hostname = socket.gethostname()


# CHANGE DIR TO SAVE FILES THE RIGTH PLACE
rawRoot     = <your scratch folder>
resultsRoot = <your results folder>
scriptsRoot = <scripts folder>

os.chdir(rawRoot) ## set series directory
# Pick all tSSS-ed fif files
fileList = [f for f in os.listdir(rawRoot) if f.endswith('tSSS.fif')]

os.chdir(script_path)
for j in fileList: #numpy.arange(0,numpy.size(fileList)):
    print j
    submit_cmd = "python analysisPipeline_clusterize.py %s %s %s" %(j, rawRoot, resultsRoot, scriptsRoot)
    subprocess.call([cmd, "1",submit_cmd]) # submit to ISIS
