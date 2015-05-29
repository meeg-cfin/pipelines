#!/bin/bash

# Script to run Freesufer recon-all on several subjects on the cluster 
# version: 0.3
# Author: mje, mads [] cnru.dk

# Loop to create a script per subject and submit to cluster
for sub in 0002 # TODO: set subject numbers
do 

# Assign variables for script and output files
    SCRIPT=sub_recon_${sub}.sh  # set script name
    sub_id=test_sub_${sub} # TODO: Change to proper subject name for the freesurfer SUBJECTS_DIR
 
# Generate a single script
cat << EOF > ${SCRIPT}
#!/bin/bash
#$ -S /bin/bash
export TERM vt100
# Make sure MNI and CFIN are in the path
PATH=$PATH:/usr/local/mni/bin:/usr/local/cfin/bin:.

# Add Freesurfer
export FREESURFER_HOME=/usr/local/freesurfer
source $FREESURFER_HOME/SetUpFreeSurfer.sh

export SUBJECTS_DIR=/projects/???
export SCRIPT_dir=/projects/???

# Change to current directory.
cd `pwd` # TODO: change to scratch or log dir

# Run the program with the parameters:
recon-all -s ${sub_id} -i $(python /projects/???/dicom_from_db.py ${sub}) -all #set path to dicom_from_db.py
EOF

# Make the new script executable
chmod u+x ${SCRIPT}

# Finally submit it to the cluster in the long.q queue
qsub -j y -q long.q ${SCRIPT}

rm ${SCRIPT} # Uncomment to delete the scripts after they are commited.

done
