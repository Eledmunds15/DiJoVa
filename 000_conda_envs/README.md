# Conda Environment Files

This project includes several Conda environment files tailored for different purposes:

- **01:** `mol_dynamics_lmp.yml` — Environment for input generation, lammps simulations, and post-processing with Ovito and other python packages

## Creating Conda Environments

To create an environment, run:

```bash
conda env create -n <env_name> -f <file.yml>
```
Example:
```bash
conda env create -n mol_dynamics_lmp -f mol_dynamics_lmp.yml
```
Activate the environment with:
```bash
conda activate <env_name>
```
## Removing Conda Environments

To remove an environment, run:
```bash
conda env remove -n <env_name>
```
Example:
```bash
conda env remove -n mol_dynamics_lmp
```