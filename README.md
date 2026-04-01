# AI-generated Left Ventricle CFD Simulations
CFD simulations using [svMultiPhysics](https://github.com/SimVascular/svMultiPhysics/) and [svZeroDSolver](https://github.com/SimVascular/svZeroDSolver/) of left ventricle geometries generated using [SDF4CHD](https://github.com/fkong7/SDF4CHD/tree/journal).
Meshes are created from the generated surfaces using SimVascular's mesher (TetGen).
The 3D LV model is coupled to a 0D LPN of the rest of the cardiovascular system. 
Initial conditions are first obtained by running a 0D simulation of the full cardiovascular system to steady state. 
The cases given here are set up to run for five cycles; steady state is observed after about two cycles.

## Requirements
Solvers:
* [svMultiPhysics](https://github.com/SimVascular/svMultiPhysics/)
* [svZeroDSolver](https://github.com/SimVascular/svZeroDSolver/)

Python packages:
* numpy
* matplotlib
* pyvista
* vtk
* pandas
* natsort

## Workflows
Scripts for different workflows are in `workflow_scripts`.
* `run_batch.sh`: run a batch of simulations. Meshes must be set up beforehand (see `setup_batch.sh`). 
    * Usage: `bash run_batch.sh $START_CASE_NUMBER $END_CASE_NUMBER`
* `run_meshconv.sh`: set up mesh convergence study meshes
* `run_sim.sh`: run simulation for given case.
    * Usage: `bash run_sim.sh $CASE_PATH`
* `setup_batch.sh`: set up a batch of simulations, creating meshes for each case
    * Usage: `bash setup_batch.sh START_CASE_NUMBER $END_CASE_NUMBER`
