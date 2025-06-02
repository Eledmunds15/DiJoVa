# --------------------------- LIBRARIES ---------------------------#
import os

import numpy as np
from matscipy.dislocation import get_elastic_constants
from matscipy.calculators.eam import EAM

from matscipy.dislocation import BCCEdge111Dislocation

from ase.io import write

from utilities import set_path, clear_dir

# --------------------------- CONFIG ---------------------------#

DATA_MASTER_DIR = '../000_output_files'

MODULE_DIR = '01_input_files'

OUTPUT_FILE = 'straight_edge_dislo.lmp'

POTENTIAL_DIR = '../00_potentials'
POTENTIAL_FILE = 'malerba.fs'

DISLO_CYL_RADIUS = 100 # Radius of the cylinder around the dislocation (Angstroms)
DISLO_LEN = 10 # Length of the dislocation (number of planes)

# --------------------------- MAIN SCRIPT ---------------------------#

def main():

    set_path() # Sets the path to the location of the current script

    #--- DIRECTORIES ---#
    potential_path = os.path.join(POTENTIAL_DIR, POTENTIAL_FILE)

    os.makedirs(DATA_MASTER_DIR, exist_ok=True)
    os.makedirs(os.path.join(DATA_MASTER_DIR, MODULE_DIR), exist_ok=True)
    clear_dir(os.path.join(DATA_MASTER_DIR, MODULE_DIR))

    output_path = os.path.join(DATA_MASTER_DIR, MODULE_DIR, OUTPUT_FILE)

    #--- MATSCIPY ---#

    eam_calc = EAM(potential_path)
    alat, C11, C12, C44 = get_elastic_constants(calculator=eam_calc, symbol='Fe', verbose='False') # Get information from the potential file for file creation
    print(f"{alat:.3f} (Angstrom), {C11:.2f}, {C12:.2f}, {C44:.2f} (GPa)") # Print information

    Fe_edge = BCCEdge111Dislocation(alat, C11, C12, C44, symbol="Fe") # Create dislocation object

    edge_bulk, edge_dislo = Fe_edge.build_cylinder(radius=DISLO_CYL_RADIUS) # Create a single plane of cylinder around the dislocation

    edge_dislo_long = edge_dislo.repeat((1,1,DISLO_LEN)) # Replicate the cylinder along the dislocation axis (z)

    print(f"Number of atoms: {len(edge_dislo_long)}") # Find the number of atoms in the sim

    write(output_path, edge_dislo_long, format="lammps-data", specorder=['Fe']) # Write the file out to lammps input file

    return None

# --------------------------- ENTRY POINT ---------------------------#

if __name__ == "__main__":

        main()