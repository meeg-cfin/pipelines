# -*- coding: utf-8 -*-
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

# change to stormdb.accss (mod. __init__.py)
from access import Query

def _parallel_task(command):
    """
        General purpose method to submit Unix executable-based analyses (e.g.
        maxfilter and freesurfer) to the shell.
        
        Parameters:
            command:    The command to execute (single string)
                                        
        Returns:        The return code (shell) of the command
    """
    #proc = subprocess.Popen([fs_cmd],stdout=subprocess.PIPE, shell=True)
    proc = subprocess.Popen([command], shell=True)
    
    proc.communicate()
    return proc.returncode

proj_code = 'MINDLAB2013_01-MEG-AttentionEmotionVisualTracking'
db=Query(proj_code)
proj_folder = os.path.join('/projects', proj_code)
scratch_folder = os.path.join(proj_folder, 'scratch')

recon_all_bin = '/opt/local/freesurfer-releases/5.3.0/bin/recon-all'
subjects_dir = os.path.join(scratch_folder, 'fs_subjects_dir')

fs_params = {'input_file': None, 'use_gpu': True, 'num_threads': 2,
        'fs_bin': recon_all_bin, 'subjects_dir': subjects_dir,
        'fs_tasks': '-all', 'force': False}

# beware that the total number of threads can then (at worst)
# be n_parallel_procs * fs_params['num_threads']
# for those fs-binaries that use openmp
n_parallel_procs = 4

included_subjects = db.get_subjects()
fs_cmd_list = []
# First build list of 
for subj in included_subjects:

    # WIP: implement check to see that mri_convert has been run
    # and T1-files exist in subjects_dir

    # this is an example of getting the DICOM files as a list
    sequence_name='t1_mprage_3D_sag'
    mr_study = db.get_studies(subj, modality='MR',unique=True)
    if not mr_study is None:
        # This is a 2D list with [series_name, series_number]
        series = db.get_series(subj, mr_study, 'MR',verbose=False)
    #### Change this to be more elegant: check whether any item in series
    #### matches sequence_name
        for ser in series:
            if sequence_name in ser:
                T1_file_names = db.get_files(subj, mr_study, 'MR',ser[1])


    # if running from raw dicom (test!)
    input_dicom = T1_file_names[0] # first DICOM file
        
    fs_cmd = 'SUBJECTS_DIR=' + fs_params['subjects_dir'] + ' ' \
            + fs_params['fs_bin'] + ' ' + fs_params['fs_tasks'] \
            + ' -s ' + subj 
            
    if input_dicom:
        fs_cmd += ' -i ' + input_dicom
    if fs_params['use_gpu']:
        fs_cmd += ' -use-gpu '
    if fs_params['num_threads']:
        fs_cmd += ' -openmp %d ' % fs_params['num_threads']

    if os.path.exists(os.path.join(fs_params['subjects_dir'],subj)) and not CLOBBER:
        print('Subject %s appears to be done, skipping (use force to overwrite)' % subj)
            
    # switch comments to test parallel submission
    fs_cmd_list.append(fs_cmd)
    #fs_cmd_list.append('echo "$(hostname) proc $$ sleeping 2 sec"; sleep 2') # for testing

# sending multiple processes away
if not FAKE:
    pool = multiprocessing.Pool(processes=n_parallel_procs)

    return_codes = pool.map(_parallel_task,fs_cmd_list)
    pool.close()
    pool.join()

elif VERBOSE:
    print("The following would execute, if this were not a FAKE run:")
    for cmd in fs_cmd_list:
        print("%s" % cmd)

