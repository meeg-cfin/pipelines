# -*- coding: utf-8 -*-
"""
Created on Tue Feb 16 13:15:38 2016
@author: kousik
Code to re-run files that weren't cleaned properly
Can use visual feedback to reject components

*** Caution ***
Copy the raw and ica solutions of files into\
a new folder. here for eg. artRej
# Run automatic ArtRej routine first
# Needs: *-raw.fif and *-ica.fif files
# Takes user input in TUI
"""

import os
import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
import mne
import numpy as np
from mne.preprocessing import create_ecg_epochs, create_eog_epochs

## which steps to run
## first steps
read = 1          # can't save filtered files, so don't run this time \
                  # consuming process every time
Filter = 1        # epochs and sensor space processing
epochIca = 0
evokeds = 0
saveICA = 1
ICAraw = 1

## set path and subs
baseRoot='/projects/<yourProj>/<folder>' # your projects folder
rawRoot     = baseRoot+'/tSSS/'          # Folder containing RAW files post-tSSS
artRejRoot  = baseRoot+'/artRej/'        # Folder containing ICA solution files(*-ica.fif) from auto-Run
resultsRoot = baseRoot+'/artRej/'        # Folder to save PDFs, RAW-clean: \
                                         # Program appends file names with '-vis' tag\
                                         # No overwrite risk
# Create results folder
try:
    os.stat(resultsRoot)
    print '*** Directory already exists'
except:
    os.mkdir(resultsRoot)       
    print '*** Directory created now'                
                
# Get ICA file list and recreate filenames of RAW, 
icaFileList = [f for f in os.listdir(artRejRoot) if f.endswith('-ica.fif')]
icaFileList.sort()
for f in np.arange(0,np.size(icaFileList)): 
    rawFileList.insert(f,icaFileList[f][:-8]+'_tSSS.fif')
    
for j in icaFileList:
    name=j[:-8]
    print name
    icacomps = mne.preprocessing.read_ica(artRejRoot+j)
    if icacomps.exclude:
        print('##################')
        print('Pre-selected comps: '+str(icacomps.exclude))
        print('##################')
        icacomps.excludeold=icacomps.exclude
        icacomps.exclude=[]
        if not icacomps.exclude:
            print('Old components copied. Exclude field cleared')    
    
    raw = mne.io.Raw(rawRoot+name+'.fif', preload=True)
    ecg_picks = mne.pick_types(raw.info, meg=False, eeg=False, eog=False, ecg=True,
                   stim=False, exclude='bads')[0]
    eog_picks = mne.pick_types(raw.info, meg=False, eeg=False, ecg=False, eog=True,
                   stim=False, exclude='bads')[0]
    meg_picks = mne.pick_types(raw.info, meg=True, eeg=False, eog=False, ecg=False,
                       stim=False, exclude='bads')               
                   
    ecg_epochs = create_ecg_epochs(raw, tmin=-.5, tmax=.5,picks=meg_picks, verbose=False)
                                   #ch_name=raw.ch_names[ecg_picks].encode('UTF8'))
    ecg_evoked = ecg_epochs.average()
    eog_evoked = create_eog_epochs(raw, tmin=-.5, tmax=.5,picks=meg_picks,
                           ch_name=raw.ch_names[eog_picks].encode('UTF8'), verbose=False).average()


    # ica topos
    source_idx = range(0, icacomps.n_components_)
    ica_plot = icacomps.plot_components(source_idx, ch_type="mag") 
    plt.waitforbuttonpress(1)
    
    title = 'Sources related to %s artifacts (red)'
    
    #ask for comps ECG
    prompt = '> '
    ecg_done = 'N'
    eog_done = 'N'
    
    while ecg_done.strip() != 'Y' and ecg_done.strip() != 'y':
        ecg_source_idx = []        
        print 'What components should be rejected as ECG comps?'
        print 'If more than one, list them each separated by a comma and a space'
        try:
            ecg_source_idx = map(int, raw_input(prompt).split(','))    
        except ValueError:
            ecg_source_idx = []
            print 'Exiting ECG - No components selected'
            break
               
        print ecg_source_idx
        
        if ecg_source_idx: 
            print ecg_source_idx
            source_plot_ecg = icacomps.plot_sources(ecg_evoked, exclude=ecg_source_idx)
            plt.waitforbuttonpress(1)
            clean_plot_ecg=icacomps.plot_overlay(ecg_evoked, exclude=ecg_source_idx)
            plt.waitforbuttonpress(1)
            print 'Clean enough?[Y/N]: '
            print ''
            print 'To terminate without selecting any components, type "N" now'
            print 'and then don''t select any components pressing ENTER'
            ecg_done = raw_input(prompt)
            plt.close(source_plot_ecg)
            plt.close(clean_plot_ecg)
   
    ecg_exclude = ecg_source_idx
    
    if ecg_source_idx:
        icacomps.exclude += ecg_source_idx
        source_plot_ecg.savefig(resultsRoot + name + 'source_plot_ecg_vis.pdf', format = 'pdf')
#        plt.waitforbuttonpress(1)  
        clean_plot_ecg.savefig(resultsRoot + name + 'clean_plot_ecg_vis.pdf', format = 'pdf')
#        plt.waitforbuttonpress(1)
  #      scores_plot_ecg.savefig(resultsRoot + name + 'scores_plot_ecg_vis.pdf', format = 'pdf')
        plt.close(source_plot_ecg)
        plt.close(clean_plot_ecg)
    else:
        print '*** No ECG components rejected...'
        
    while eog_done.strip() != 'Y' and eog_done.strip() != 'y':
        eog_source_idx = []        
        print 'What components should be rejected as EOG comps?'
        print 'If more than one, list them each separated by a comma and a space'
        try:
            eog_source_idx = map(int, raw_input(prompt).split(','))    
        except ValueError:
            eog_source_idx = []
            print 'Exiting EOG - No components selected'
            break
               
        print eog_source_idx
        
        if eog_source_idx: 
            print eog_source_idx
            source_plot_eog = icacomps.plot_sources(eog_evoked, exclude=eog_source_idx)
            plt.waitforbuttonpress(1)
            clean_plot_eog=icacomps.plot_overlay(eog_evoked, exclude=eog_source_idx)
            plt.waitforbuttonpress(1)
            print 'Clean enough?[Y/N]: '
            print ''
            print 'To terminate without selecting any components, type "N" now'
            print 'and then don''t select any components pressing ENTER'
            eog_done = raw_input(prompt)
            plt.close(source_plot_eog)
            plt.close(clean_plot_eog)
    eog_exclude = eog_source_idx
    
    if eog_source_idx:
        icacomps.exclude += eog_source_idx
        source_plot_eog.savefig(resultsRoot + name + 'source_plot_eog_vis.pdf', format = 'pdf')
#        plt.waitforbuttonpress(1)
        clean_plot_eog.savefig(resultsRoot + name + 'clean_plot_eog_vis.pdf', format = 'pdf')
#        plt.waitforbuttonpress(1)
#        scores_plot_eog.savefig(resultsRoot + name + 'scores_plot_eog_vis.pdf', format = 'pdf')
        plt.close(source_plot_eog)
        plt.close(clean_plot_eog) 
    else:
        print '*** No EOG components rejected...'
    
    print '############'    
    print('*** Excluding following components: ', icacomps.exclude)        
    plt.close('all')
    
    raw_ica = icacomps.apply(raw)
    raw_ica.save(resultsRoot + name + '_ica-vis-raw.fif', overwrite=False,verbose=False)
    #ica.save(saveRoot + name + '-ica.fif')
