from __future__ import print_function
"""
@author: cjb
"""
CLOBBER = False
FAKE    = False
VERBOSE = True

import os, sys
import errno
import subprocess
import multiprocessing
# ENH: install "official" version of stormdb on isis/hyades
path_to_stormdb = '/volatile/cjb/stormdb'
sys.path.append(path_to_stormdb)

# change to stormdb.access (mod. __init__.py)
from access import Query

import numpy as np

proj_code = 'MEG_EEG-Training'

db=Query(proj_code)
proj_folder = os.path.join('/projects', proj_code)
scratch_folder = os.path.join(proj_folder, 'scratch')

recon_all_bin = '/opt/local/freesurfer-releases/5.3.0/bin/recon-all'
subjects_dir = os.path.join(scratch_folder, 'fs_subjects_dir')

included_subjects = db.get_subjects()
# just test with first one!
included_subjects = included_subjects[0]

for sub in included_subjects:

    # this is an example of getting the DICOM files as a list
    sequence_name='t1_mprage_3D_sag'
    mr_study = db.get_studies(sub, modality='MR',unique=True)
    if not mr_study is None:
        # This is a 2D list with [series_name, series_number]
        series = db.get_series(sub, mr_study, 'MR',verbose=False)
    #### Change this to be more elegant: check whether any item in series
    #### matches sequence_name
        for ser in series:
            if sequence_name in ser:
                T1_file_names = db.get_files(sub, mr_study, 'MR',ser[1])

    input_dicom = T1_file_names[0] # first DICOM file

    bash_script = ['#!/usr/bin/env bash']
    # have to explicitly source bashrc (non-login shell)
    bash_script.append('source ~/.bashrc')
    bash_script.append('use mne') # set paths
    bash_script.append('export SUBJECTS_DIR='+subjects_dir)
    bash_script.append('export SCRIPT=sub_recon_'+ sub + '.sh')
    bash_script.append('export SCRIPT_dir='+proj_folder+'/scripts/mads_test_scripts')

    bash_script.append('export SUBJECT=' + sub)

    bash_script.append('recon-all -s ' + sub + '-i ' + input_dicom + ' -all')
    # Can do some exit value checking too...
    #bash_script.append('if [[ $? != 0 ]] ; then exit 1; fi')
	
    # example of how to enter a multi-line bash command
#    cmd = '''
#cd ${SUBJECTS_DIR}/${SUBJECT}/bem
#ln -s watershed/${SUBJECT}_inner_skull_surface ${SUBJECT}-inner_skull.surf
#ln -s watershed/${SUBJECT}_outer_skin_surface ${SUBJECT}-outer_skin.surf
#ln -s watershed/${SUBJECT}_outer_skull_surface ${SUBJECT}-outer_skull.surf
#cd ''' + ad._project_folder
#    bash_script.append(cmd)
    
