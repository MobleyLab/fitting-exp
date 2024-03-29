#!/bin/bash
#SBATCH -J iter24_sage_targets
#SBATCH -p standard
#SBATCH -t 200:00:00
#SBATCH --nodes=1
#SBATCH --cpus-per-task=1
#SBATCH --mem=10000mb
#SBATCH --account dmobley_lab
#SBATCH --export ALL
#SBATCH --mail-user=pbehara@uci.edu
#SBATCH --constraint=fastscratch

rm -rf /tmp/$SLURM_JOB_NAME
source $HOME/.bashrc
eval "$(/opt/apps/anaconda/2020.07/bin/conda shell.bash hook)"
conda activate fb_192

export SLURM_TMPDIR=/tmp
export TMPDIR=$SLURM_TMPDIR/$SLURM_JOB_NAME
mkdir  -p  $SLURM_TMPDIR/$SLURM_JOB_NAME
rsync  -avzIi  $SLURM_SUBMIT_DIR/optimize.in  $SLURM_TMPDIR/$SLURM_JOB_NAME
rsync  -avzIi  $SLURM_SUBMIT_DIR/targets.tar.gz  $SLURM_TMPDIR/$SLURM_JOB_NAME
rsync  -avzIi  $SLURM_SUBMIT_DIR/forcefield  $SLURM_TMPDIR/$SLURM_JOB_NAME
cd $SLURM_TMPDIR/$SLURM_JOB_NAME

tar -xzvf targets.tar.gz

datadir=$(pwd)
mkdir -p $SLURM_SUBMIT_DIR/worker_logs
echo $(hostname) > $SLURM_SUBMIT_DIR/host

export OMP_NUM_THREADS=1
export MKL_NUM_THREADS=1

if ForceBalance.py optimize.in ; then
   rsync  -avzIi --exclude="optimize.tmp" --exclude="optimize.bak" --exclude="targets" $SLURM_TMPDIR/$SLURM_JOB_NAME/* $SLURM_SUBMIT_DIR > copy.log
   rm -rf $SLURM_TMPDIR/$SLURM_JOB_NAME
fi

echo "All done"
