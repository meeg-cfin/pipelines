# mne-python-preproc
First go at a structured pipeline for the first preprocessing steps for MEG data
(tested on three MEG datasets with PD patients and healthy controls)

Contains the following steps:
Filtering
ICA-based rejection of ECG and EOG artifacts
  - involves plotting and saving figures for this process
  - as well as an interactive function for inspecting the rejected components
