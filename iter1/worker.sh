#!/usr/bin/env bash
#SBATCH -J fit-worker
#SBATCH -p free
#SBATCH -t 10:00:00
#SBATCH --nodes=1
#SBATCH --ntasks=8
#SBATCH --cpus-per-task=1
#SBATCH --mem-per-cpu=4gb
#SBATCH --array=1-400
#SBATCH --account dmobley_lab
#SBATCH --export ALL
#SBATCH -o worker_logs/slurm-%A_%a.out
#SBATCH --requeue

# the max jobs for my user is 150

eval "$(/opt/apps/anaconda/2020.07/bin/conda shell.bash hook)"
conda activate /dfs6/pub/pbehara/bin/conda/fb_env
host="$(cat ./host)"
export OMP_NUM_THREADS=1
export MKL_NUM_THREADS=1

tmpdir=/dev/shm/pbehara/fb-worker
mkdir -p $tmpdir
for i in $(seq  $SLURM_NTASKS ); do
	
	work_queue_worker --cores 1 -s $(mktemp -d -p $tmpdir ) --memory=$(( 4096 * 2 )) --gpus=0 $host 55135 &
done
wait
#work_queue_worker --cores 1 -s $(mktemp -d -p /dev/shm/ ) --memory=$(( 4096 )) --gpus=0 $host 55125 &
#work_queue_worker --cores 1 -s $(mktemp -d -p /dev/shm/ ) --memory=$(( 4096 )) --gpus=0 $host 55125 &
#work_queue_worker --cores 1 -s $(mktemp -d -p /dev/shm/ ) --memory=$(( 4096 )) --gpus=0 $host 55125 &

#wait
