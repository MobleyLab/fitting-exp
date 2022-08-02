# Parallelized benchmark scripts 

Python scripts to run the benchmarks are available at this repo: https://github.com/openforcefield/openff-sage/tree/main/inputs-and-results/benchmarks/qc-opt-geo. 
Here are the slurmscripts to run on the cluster. Step 1 needs to be run only once and after the large sdf file is generated it is chopped into chunks (here 250 of them) and MM optimizations are run in parallel especially steps 02-b and 03-a. In step 04 for the functional-group-wise analysis checkmol executbale should be in the path. Checkmol can be downloaded from https://homepage.univie.ac.at/norbert.haider/download/chemistry/checkmol/?dir=bin. 

Some tips:
- Steps 02b and 03a can be combined into one script, both of them run on chunks of data
- Steps 03b and 04 can be in a single slurmscript
- 03-force-field.json should be populated before running step-03a
- 03-outputs should be empty before running step-03a since the data gets appended to the existing files, so if you're re-running be cautious
- check the number of final optimized geometries to be same as the input QM (73301), some slurm runs may fail silently due to memory issues and you may not notice it
- File `ddE_plot_with_ranges.ipynb` if you want to plot the ddE in ranges of energy differences, can include in the main plot script (to-do)
