#!/bin/bash

# Script to run Freesufer recon-all on several subjects on the cluster 
# version: 0.1
# Author: mje, mads [at] cnru.dk

# Loop to create a script per subject and submit to cluster
for sub in # TODO: set subject numbers
do 

# Assign variables for script and output files
    SCRIPT=sub_recon_${sub}.sh

# Generate a single script
cat << EOF > ${SCRIPT}
#!/bin/bash
#$ -S /bin/bash
export TERM vt100
# Make sure MNI and CFIN are in the path
PATH=$PATH:/usr/local/mni/bin:/usr/local/cfin/bin:. # FIXME: Check this Path is right!

# Add Freesurfer
export FFREESURFER_HOME=/usr/local/freesurfer # FIXME: check path
source $FREESURFER_HOME/SetUpFreeSurfer.sh

export SUBJECTS_DIR=/project/SOMETHING # TODO: set the path 

# Change to current directory.
cd `pwd` # TODO: change to scratch or log dir

# Run the program with the parameters:
recon-all -subjid -all # TODO: add params use "no-isrunning" flag?
EOF

# Make the new script executable
chmod u+x ${SCRIPT}

# Finally submit it to the cluster in the long.q queue
qsub -j y -q long.q ${SCRIPT}

# rm ${SCRIPT} # Uncomment to delete the scripts after they are commited.

done
