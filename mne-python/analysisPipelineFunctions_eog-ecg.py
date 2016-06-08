# -*- coding: utf-8 -*-
"""
Adapted on Aug 2015)
(Orig created on Wed Mar 19 09:34:24 2014)

@orig_author: lau
@author: andreas & niels christian
@author: kousik
"""
'''ANALYSIS PIPELINE FUNCTIONS'''
' Many of these are NOT used!!! '

## import libraries
import mne
import os
import numpy as np
import scipy as sci
import matplotlib
## Set backends for plotting
matplotlib.use('TkAgg')
print('TkAgg')
import matplotlib.pyplot as plt
## Import mne specific modules
from mne.io import Raw
from mne.preprocessing import ICA
from mne.preprocessing import create_ecg_epochs, create_eog_epochs
from mne.viz import plot_evoked_topomap


''' PREPROCESSING PART '''
def readRawList(fileList,preload=False):
    '''Read in fileList, and choose whether to preload. Returns "raw"'''
    raw = Raw(fileList,preload=preload) ## read in files
    return raw
 
def filterRaw(raw,l_freq,h_freq,method='iir',save=False):
    '''Filter raw file at the given frequencies and with the given method'''
    raw.filter(l_freq=l_freq,h_freq=h_freq,method=method)
    if save:
        raw.save('filt' + str(l_freq) + '_' + str(h_freq) +\
                'raw_tsss_at_mc.fif')
                
def splitSaveRaw(raw,splits,fnamePattern):
    for iSplit, (tmin,tmax) in enumerate(splits):
        raw.copy().crop(tmin,tmax).save(fnamePattern % iSplit)
    
def findEvents(raw,stim_channel='STI101',verbose=False,
                        min_duration=0.001):
     '''Find Target ids'''                           
     events = mne.find_events(raw=raw,stim_channel=stim_channel,
                                verbose=verbose,min_duration=min_duration) 
     return events                                   
                                                                     
  
''' cf. http://martinos.org/mne/stable/auto_examples/preprocessing/plot_ica_from_raw.html for help on integrating ecg-identification as well '''    
def runICA(raw,saveRoot,name):

    saveRoot = saveRoot    
    icaList = [] 
    ica = []
    n_max_ecg = 3   # max number of ecg components 
#    n_max_eog_1 = 2 # max number of vert eog comps
#    n_max_eog_2 = 2 # max number of horiz eog comps          
    ecg_source_idx, ecg_scores, ecg_exclude = [], [], []
    eog_source_idx, eog_scores, eog_exclude = [], [], []
    #horiz = 1       # will later be modified to horiz = 0 if no horizontal EOG components are identified                   
    ica = ICA(n_components=0.90,n_pca_components=64,max_pca_components=100,noise_cov=None)
        
    ica.fit(raw)
    #*************
    eog_picks = mne.pick_types(raw.info, meg=False, eeg=False, stim=False, eog=True, ecg=False, emg=False)[0]
    ecg_picks = mne.pick_types(raw.info, meg=False, eeg=False, stim=False, ecg=True, eog=False, emg=False)[0]
    ica_picks = mne.pick_types(raw.info, meg=True, eeg=False, eog=False, ecg=False,
                   stim=False, exclude='bads')
    ecg_epochs = create_ecg_epochs(raw, tmin=-.5, tmax=.5, picks=ica_picks)
    ecg_evoked = ecg_epochs.average()
    eog_evoked = create_eog_epochs(raw, tmin=-.5, tmax=.5, picks=ica_picks).average()

    ecg_source_idx, ecg_scores = ica.find_bads_ecg(ecg_epochs, method='ctps')
    eog_source_idx, eog_scores = ica.find_bads_eog(raw,ch_name=raw.ch_names[eog_picks].encode('ascii', 'ignore'))
       
    # defining a title-frame for later use
    title = 'Sources related to %s artifacts (red)'

    # extracting number of ica-components and plotting their topographies
    source_idx = range(0, ica.n_components_)
    ica_plot = ica.plot_components(source_idx, ch_type="mag")                                           

    # select ICA sources and reconstruct MEG signals, compute clean ERFs
    # Add detected artefact sources to exclusion list
    # We now add the eog artefacts to the ica.exclusion list
    if not ecg_source_idx:
        print("No ECG components above threshold were identified for subject " + name +
        " - selecting the component with the highest score under threshold")
        ecg_exclude = [np.absolute(ecg_scores).argmax()]
        ecg_source_idx=[np.absolute(ecg_scores).argmax()]
    elif ecg_source_idx:
        ecg_exclude += ecg_source_idx[:n_max_ecg]
    ica.exclude += ecg_exclude

    if not eog_source_idx:
        if np.absolute(eog_scores).any>0.3:
            eog_exclude=[np.absolute(eog_scores).argmax()]
            eog_source_idx=[np.absolute(eog_scores).argmax()]
            print("No EOG components above threshold were identified " + name +
            " - selecting the component with the highest score under threshold above 0.3")
        elif not np.absolute(eog_scores).any>0.3:
            eog_exclude=[]
            print("No EOG components above threshold were identified" + name)
    elif eog_source_idx:
         eog_exclude += eog_source_idx

    ica.exclude += eog_exclude

    print('########## saving')
    if len(eog_exclude) == 0:
        if len(ecg_exclude) == 0:
            ica_plot.savefig(saveRoot + name + '_comps_eog_none-ecg_none' + '.pdf', format = 'pdf')
        elif len(ecg_exclude) == 1:
            ica_plot.savefig(saveRoot + name + '_comps_eog_none-ecg' + map(str, ecg_exclude)[0] + '.pdf', format = 'pdf')
        elif len(ecg_exclude) == 2:
            ica_plot.savefig(saveRoot + name + '_comps_eog_none-ecg' + map(str, ecg_exclude)[0] + '_' + map(str, ecg_exclude)[1] + '.pdf', format = 'pdf')
        elif len(ecg_exclude) == 3:
            ica_plot.savefig(saveRoot + name + '_comps_eog_none-ecg' + map(str, ecg_exclude)[0] + '_' + map(str, ecg_exclude)[1] + '_' + map(str, ecg_exclude)[2] + '.pdf', format = 'pdf')
    elif len(eog_exclude) == 1:
        if len(ecg_exclude) == 0:
            ica_plot.savefig(saveRoot + name + '_comps_eog' + map(str, eog_exclude)[0] +
            '-ecg_none' + '.pdf', format = 'pdf')
        elif len(ecg_exclude) == 1:
            ica_plot.savefig(saveRoot + name + '_comps_eog' + map(str, eog_exclude)[0] +
            '-ecg' + map(str, ecg_exclude)[0] + '.pdf', format = 'pdf')
        elif len(ecg_exclude) == 2:
            ica_plot.savefig(saveRoot + name + '_comps_eog' + map(str, eog_exclude)[0] +
            '-ecg' + map(str, ecg_exclude)[0] + '_' + map(str, ecg_exclude)[1] + '.pdf', format = 'pdf')
        elif len(ecg_exclude) == 3:
            ica_plot.savefig(saveRoot + name + '_comps_eog' + map(str, eog_exclude)[0] +
            '-ecg' + map(str, ecg_exclude)[0] + '_' + map(str, ecg_exclude)[1] + '_' + map(str, ecg_exclude)[2] + '.pdf', format = 'pdf')
    elif len(eog_exclude) == 2:
        if len(ecg_exclude) == 0:
            ica_plot.savefig(saveRoot + name + '_comps_eog' + map(str, eog_exclude)[0] + '_' + map(str, eog_exclude)[1] +
            '-ecg_none' + '.pdf', format = 'pdf')
        elif len(ecg_exclude) == 1:
            ica_plot.savefig(saveRoot + name + '_comps_eog' + map(str, eog_exclude)[0] + '_' + map(str, eog_exclude)[1] +
            '-ecg' + map(str, ecg_exclude)[0] + '.pdf', format = 'pdf')
        elif len(ecg_exclude) == 2:
            ica_plot.savefig(saveRoot + name + '_comps_eog' + map(str, eog_exclude)[0] + '_' + map(str, eog_exclude)[1] +
            '-ecg' + map(str, ecg_exclude)[0] + '_' + map(str, ecg_exclude)[1] + '.pdf', format = 'pdf')
        elif len(ecg_exclude) == 3:
            ica_plot.savefig(saveRoot + name + '_comps_eog' + map(str, eog_exclude)[0] + '_' + map(str, eog_exclude)[1] +
            '-ecg' + map(str, ecg_exclude)[0] + '_' + map(str, ecg_exclude)[1] + '_' + map(str, ecg_exclude)[2] + '.pdf', format = 'pdf')
    
    # plot the scores for the different components highlighting in red that/those related to ECG
    scores_plots_ecg=ica.plot_scores(ecg_scores, exclude=ecg_source_idx, title=title % 'ecg')
    scores_plots_ecg.savefig(saveRoot + name + '_ecg_scores.pdf', format = 'pdf')
    scores_plots_eog=ica.plot_scores(eog_scores, exclude=eog_source_idx, title=title % 'eog')
    scores_plots_eog.savefig(saveRoot + name + '_eog_scores.pdf', format = 'pdf')
    source_source_ecg=ica.plot_sources(ecg_evoked, exclude=ecg_source_idx)
    source_source_ecg.savefig(saveRoot + name + '_ecg_source.pdf', format = 'pdf')
    #ax = plt.subplot(2,1,2)
    source_clean_ecg=ica.plot_overlay(ecg_evoked, exclude=ecg_source_idx)
    source_clean_ecg.savefig(saveRoot + name + '_ecg_clean.pdf', format = 'pdf')
    #clean_plot.savefig(saveRoot + name + '_ecg_clean.pdf', format = 'pdf')
        
    #if len(eog_exclude) > 0:
    source_source_eog=ica.plot_sources(eog_evoked, exclude=eog_source_idx)
    source_source_eog.savefig(saveRoot + name + '_eog_source.pdf', format = 'pdf')
    source_clean_eog=ica.plot_overlay(eog_evoked, exclude=eog_source_idx)
    source_clean_eog.savefig(saveRoot + name + '_eog_clean.pdf', format = 'pdf')
   
    
    overl_plot = ica.plot_overlay(raw)
    overl_plot.savefig(saveRoot + name + '_overl.pdf', format = 'pdf')
    
    event_id = 999
    ecg_events, _, _ = mne.preprocessing.find_ecg_events(raw, event_id,
                             ch_name=raw.ch_names[ecg_picks].encode('UTF8'))
    picks = mne.pick_types(raw.info, meg=False, eeg=False, stim=False, ecg=True)

    tmin, tmax = -0.1, 0.1
    epochs_ecg = mne.Epochs(raw, ecg_events, event_id, tmin, tmax,picks=picks)
    data_ecg = epochs_ecg.get_data()

    event_id = 998
    eog_events = mne.preprocessing.find_eog_events(raw, event_id,
                                   ch_name=raw.ch_names[eog_picks].encode('UTF8'))
    picks = mne.pick_types(raw.info, meg=False, eeg=False, stim=False, eog=True,
                           exclude='bads')
    tmin, tmax = -0.5, 0.5
    epochs_eog = mne.Epochs(raw, eog_events, event_id, tmin, tmax,picks=[picks[0]])#,
    data_eog = epochs_eog.get_data()

    plSize = 1
    pltRes = 128
    ecg_eogAvg=plt.figure(figsize=(20,10))
    ax = plt.subplot(2,3,1)
    plt.plot(1e3 * epochs_ecg.times, np.squeeze(data_ecg).T)
    plt.xlabel('Times (ms)')
    plt.title('ECG')
    plt.ylabel('ECG')
    plt.show()                   
    ax2 = plt.subplot(2,3,2)
    plot_evoked_topomap(ecg_evoked, times=0, average=0.02, ch_type='mag',colorbar=False,
                        size=plSize, res=pltRes,
                        axes=ax2)
    ax3= plt.subplot(2,3,3)
    plot_evoked_topomap(ecg_evoked, times=0, average=0.02, ch_type='grad',colorbar=False,
                        size=plSize, res=pltRes,                            
                        axes=ax3)
    ax = plt.subplot(2,3,4)
    plt.plot(1e3 * epochs_eog.times, np.squeeze(data_eog).T)
    plt.xlabel('Times (ms)')
    plt.title('EOG')
    plt.ylabel('EOG')
    ax = plt.subplot(2,3,5)
    plot_evoked_topomap(eog_evoked, times=0, average=0.05, ch_type='mag',colorbar=False,
                        size=plSize, res=pltRes,                            
                        axes=ax)
    ax = plt.subplot(2,3,6)
    plot_evoked_topomap(eog_evoked, times=0, average=0.05, ch_type='grad',colorbar=False,
                size=plSize, res=pltRes, show=False,                            
                axes=ax)
    plt.tight_layout()
    ecg_eogAvg.savefig(saveRoot + name +'_ecg_eog_Avg.pdf',format = 'pdf')
            
    plt.close('all')
    ## restore sensor space data
    icaList = ica.apply(raw)
    return(icaList, ica)

def saveRaw(raw,ica,saveRoot,name):
    raw.save(saveRoot + name + '_ica-raw.fif', overwrite=False)
    ica.save(saveRoot + name + '-ica.fif')
