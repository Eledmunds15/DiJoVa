# --------------------------- LIBRARIES ---------------------------#
import os

import numpy as np
from matscipy.dislocation import get_elastic_constants
from matscipy.calculators.eam import EAM

from matscipy.dislocation import BCCEdge111Dislocation

from ase.io import write

# --------------------------- CONFIG ---------------------------#

OUTPUT_FILE = 'straight_edge_dislo.lmp'

POTENTIAL_DIR = '../00_potentials'
POTENTIAL_FILE = 'malerba.fs'

DISLO_CYL_RADIUS = 150 # Radius of the cylinder around the dislocation (Angstroms)
DISLO_LEN = 40 # Length of the dislocation (number of planes)

# --------------------------- MAIN SCRIPT ---------------------------#

def main():

    set_path() # Sets the path to the location of the current script
    del_file(OUTPUT_FILE) # Deletes any previous input file

    #--- DIRECTORIES ---#
    potential_path = os.path.join(POTENTIAL_DIR, POTENTIAL_FILE)

    #--- MATSCIPY ---#

    eam_calc = EAM(potential_path)
    alat, C11, C12, C44 = get_elastic_constants(calculator=eam_calc, symbol='Fe', verbose='False') # Get information from the potential file for file creation
    print(f"{alat:.3f} (Angstrom), {C11:.2f}, {C12:.2f}, {C44:.2f} (GPa)") # Print information

    Fe_edge = BCCEdge111Dislocation(alat, C11, C12, C44, symbol="Fe") # Create dislocation object

    edge_bulk, edge_dislo = Fe_edge.build_cylinder(radius=DISLO_CYL_RADIUS) # Create a single plane of cylinder around the dislocation

    edge_dislo_long = edge_dislo.repeat((1,1,DISLO_LEN)) # Replicate the cylinder along the dislocation axis (z)

    print(f"Number of atoms: {len(edge_dislo_long)}") # Find the number of atoms in the sim

    write(OUTPUT_FILE, edge_dislo_long, format="lammps-data", specorder=['Fe']) # Write the file out to lammps input file

    return None

# --------------------------- UTILITIES ---------------------------#

def set_path():

    filepath = os.path.dirname(os.path.abspath(__file__))
    os.chdir(filepath)
    print(f'Working directory set to: {filepath}')

def del_file(filepath):
     
    abs_path = os.path.abspath(filepath)
    
    if not os.path.exists(abs_path):
        raise FileNotFoundError(f"The file '{filepath}' does not exist.")
    
    if not os.path.isfile(abs_path):
        raise ValueError(f"The path '{filepath}' is not a file.")
    
    try:
        os.remove(abs_path)
        print(f"Deleted file: {abs_path}")
    except Exception as e:
        print(f"Failed to delete '{abs_path}'. Reason: {e}")

# --------------------------- ENTRY POINT ---------------------------#

if __name__ == "__main__":

        main()