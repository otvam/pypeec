#!/bin/bash

# ############### Slurm commands
#SBATCH --job-name="bench"
#SBATCH --output="bench.log"
#SBATCH --time="1-0"
#SBATCH --mem="48G"
#SBATCH --nodes="1"
#SBATCH --ntasks-per-node="32"
#SBATCH --mail-type="FAIL"

# ############### init exit code
ret=0

# ############### environment variables
export PYTHONLOGGER="config/logger.ini"
export PYTHONUNBUFFERED="1"
export PARALLEL="32"

echo "================================== bench - `date -u +"%D %H:%M:%S"`"

echo "==================== PARAM"
echo "JOB TAG      : bench"
echo "HOSTNAME     : $HOSTNAME"

echo "==================== TIME"
echo "DATE GEN     : `date -u +"%D : %H:%M:%S" -d @1723220441`"
echo "DATE RUN     : `date -u +"%D : %H:%M:%S" -d @$(date -u +%s)`"

echo "==================== SLURM"
echo "JOB ID       : $SLURM_JOB_ID"
echo "JOB NAME     : $SLURM_JOB_NAME"
echo "JOB NODE     : $SLURM_JOB_NODELIST"

echo "==================== RUN: conda load"
source /optnfs/common/miniconda3/etc/profile.d/conda.sh
ret=$(( ret || $? ))

echo "==================== RUN: conda activate"
conda activate /dartfs-hpc/rc/home/8/f005fc8/.conda/envs/pypeec
ret=$(( ret || $? ))

echo "==================== RUN: run script"
python run_single.py
ret=$(( ret || $? ))

echo "================================== bench - `date -u +"%D %H:%M:%S"`"

# ############### exit with status
exit $ret
