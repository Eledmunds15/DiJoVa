# DiJoVa

## Jog Nucleation, Migration, and Pipe Diffusion Studies with LAMMPS

**DiJoVa** is a research-oriented project designed to simulate and analyze dislocation jog behavior in crystalline materials using the LAMMPS molecular dynamics simulator. It includes molecular static and dynamic simulations of jog nucleation, migration, and pipe diffusion, with the goal of deepening our understanding of dislocation dynamics at the atomic scale and dislocation interactions with point-defects (such as vacancies and self-interstitials).

---

## Overview

The repository is organized into modular directories, each corresponding to a phase in the simulation and analysis workflow:

- `000_conda_envs/` – Conda environment setup files  
- `00_potentials/` – Interatomic potential files for LAMMPS  
- `01_input_files/` – Scripts for generating initial simulation inputs  
- `02_minimize_dislo/` – Dislocation energy minimization scripts  
- `03_dislo_analysis/` – Tools for analyzing dislocations  
- `04_jog_creation/` – Methods for introducing jogs  
- `05_jog_stability/` – Simulations to evaluate jog stability  
- `06_dynamics_analysis/` – Tools for analyzing jog migration and pipe diffusion  

---

## Getting Started

### Prerequisites

- Python 3.x  
- Conda (Anaconda or Miniconda)  

---

## Installation

Clone the repository:

```bash
git clone https://github.com/Eledmunds15/DiJoVa.git
cd DiJoVa
```

Set up the Conda environments:

```bash
conda env create -f 000_conda_envs/analysis.yml
conda env create -f 000_conda_envs/lammps.yml
conda env create -f 000_conda_envs/matscipy.yml
```
Activate an environment:
```bash
conda activate <environment-name>
```
Replace <environment-name> with one of the environment names defined above.

## Running Scripts

You can run scripts directly from the project root (DiJoVa/).

Without MPI:
```bash
python -m 01_input_files.create_input_cylinder
```
With MPI (adjust -np to your available processors):
```bash
mpirun -np 4 python -m 02_minimize_dislo.minimize
```
## Directory Structure

DiJoVa/
├── 000_conda_envs/
├── 00_potentials/
├── 01_input_files/
├── 02_minimize_dislo/
├── 03_dislo_analysis/
├── 04_jog_creation/
├── 05_jog_stability/
├── 06_dynamics_analysis/
├── utilities.py
├── __init__.py
└── README.md

## License

This project is licensed under the MIT License. See the LICENSE file for more information.

## Acknowledgments and Extra Info

This project supports ongoing research into dislocation dynamics in materials science. It leverages the LAMMPS simulator and builds on prior work in atomistic modeling of crystalline defects.