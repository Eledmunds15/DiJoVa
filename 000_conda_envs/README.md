## Conda Environment Files

This project includes several Conda environment files tailored for different purposes:

- **01:** `analysis.yml` — Environment for data analysis  
- **02:** `lammps.yml` — Environment for LAMMPS simulations  
- **03:** `matscipy.yml` — Environment for Matscipy tools  

### Creating Conda Environments

To create an environment, run:

```bash
conda env create -n <env_name> -f <file.yml>

Example:

conda env create -n analysis -f analysis.yml

Activate the environment with:

conda activate <env_name>

Removing Conda Environments

To remove an environment, run:

conda env remove -n <env_name>

Example:

conda env remove -n analysis