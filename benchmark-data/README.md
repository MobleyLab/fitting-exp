# Parallelized benchmark scripts 

Python scripts to run the benchmarks are available at this repo: https://github.com/openforcefield/openff-sage/tree/main/inputs-and-results/benchmarks/qc-opt-geo. 
Here are the slurmscripts to run on the cluster. Step 1 needs to be run only once and after the large sdf file is generated it is chopped into chunks (here 250 of them) and MM optimizations are run in parallel especially steps 02-b and 03-a. In step 04 for the functional-group-wise analysis checkmol executbale should be in the path. Checkmol can be downloaded from https://homepage.univie.ac.at/norbert.haider/download/chemistry/checkmol/?dir=bin. 

