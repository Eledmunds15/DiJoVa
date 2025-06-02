# --------------------------- LIBRARIES ---------------------------#
import os
import numpy as np
from mpi4py import MPI
from lammps import lammps, PyLammps

from utilities import set_path, clear_dir

# --------------------------- CONFIG ---------------------------#

MASTER_DATA_DIR = '../000_output_files'

INPUT_DIR = '02_minimize_dislo/min_input'
INPUT_FILE = 'straight_edge_dislo.lmp'

MODULE_DIR = '04_vacancy_pop'
DUMP_DIR = 'min_dump'
OUTPUT_DIR = 'min_input'

CLEAR = True
MULTIPLE = False
ATOMS_TO_DELETE = 10 # Takes a list of integer values which determine the number of atoms it will delete.

POTENTIAL_DIR = '../00_potentials'
POTENTIAL_FILE = 'malerba.fs'

DISLO_CORE_RADIUS = 5
DISLO_OUTER_RADIUS = 6

ENERGY_TOL = 1e-6
FORCE_TOL = 1e-8

# --------------------------- MINIMIZATION ---------------------------#

def main(atoms_to_delete):

    #--- INITIALISE MPI ---#
    comm = MPI.COMM_WORLD
    rank = comm.Get_rank()
    size = comm.Get_size()

    set_path()

    if rank == 0:
        os.makedirs(MASTER_DATA_DIR, exist_ok=True)
        os.makedirs(os.path.join(MASTER_DATA_DIR, MODULE_DIR), exist_ok=True)

        dump_dir = os.path.join(MASTER_DATA_DIR, MODULE_DIR, DUMP_DIR)
        output_dir = os.path.join(MASTER_DATA_DIR, MODULE_DIR, OUTPUT_DIR)

        os.makedirs(dump_dir, exist_ok=True)
        os.makedirs(output_dir, exist_ok=True)

        input_filepath = os.path.join(MASTER_DATA_DIR, INPUT_DIR, INPUT_FILE)

        output_file = 'straight_edge_dislo.lmp'
        dump_file = 'straight_edge_dislo_dump'

        output_filepath = os.path.join(output_dir, output_file)
        dump_filepath = os.path.join(dump_dir, dump_file)

        potential_path = os.path.join(POTENTIAL_DIR, POTENTIAL_FILE)

    else:
        # For other ranks, initialize variables to None or empty strings
        dump_dir = None
        output_dir = None
        input_filepath = None
        output_filepath = None
        dump_filepath = None
        potential_path = None

    # Now broadcast all variables from rank 0 to all ranks
    dump_dir = comm.bcast(dump_dir, root=0)
    output_dir = comm.bcast(output_dir, root=0)
    input_filepath = comm.bcast(input_filepath, root=0)
    output_filepath = comm.bcast(output_filepath, root=0)
    dump_filepath = comm.bcast(dump_filepath, root=0)
    potential_path = comm.bcast(potential_path, root=0)

    #--- LAMMPS SCRIPT ---#
    lmp = lammps()
    L = PyLammps(ptr=lmp)

    L.log(os.path.join(MASTER_DATA_DIR, MODULE_DIR, 'log.lammps'))

    L.units('metal') # Set units style
    L.atom_style('atomic') # Set atom style

    L.command('boundary f f p') # Set the boundaries of the simulation

    L.read_data(input_filepath) # Read input file

    L.pair_style('eam/fs') # Set the potential style
    L.pair_coeff('*', '*', potential_path, 'Fe') # Select the potential

    #--- Find box bounds ---#
    box_bounds = lmp.extract_box()

    box_min = box_bounds[0]
    box_max = box_bounds[1]

    xmin, xmax = box_min[0], box_max[0]
    ymin, ymax = box_min[1], box_max[1]
    zmin, zmax = box_min[2], box_max[2]

    sim_box_center = [np.mean([xmin, xmax]), np.mean([ymin, ymax]), np.mean([zmin, zmax])]

    #--- Group atoms together ---#

    L.group('fe_atoms', 'type', 1) # Group all atoms

    L.region('dislo_small_reg', 'cylinder', 'z', sim_box_center[0], sim_box_center[1], DISLO_CORE_RADIUS, 'INF', 'INF')
    L.region('dislo_big_reg', 'cylinder', 'z', sim_box_center[0], sim_box_center[1], DISLO_OUTER_RADIUS, 'INF', 'INF')
    
    L.group('dislo_core_atoms', 'region', 'dislo_small_reg')
    L.group('dislo_region_atoms', 'region', 'dislo_big_reg')
    
    L.group('vacancy_region', 'subtract', 'dislo_region_atoms', 'dislo_core_atoms')

    L.delete_atoms('random', 'count', atoms_to_delete, 'yes', 'vacancy_region', 'NULL', 12343)

    L.compute('peratom', 'all', 'pe/atom') # Set a compute to track the peratom energy

    L.minimize(ENERGY_TOL, FORCE_TOL, 1000, 10000) # Execute minimization

    L.write_dump('all', 'custom', dump_filepath, 'id', 'x', 'y', 'z', 'c_peratom') # Write a dumpfile containing atom positions and pot energies
    L.write_data(output_filepath) # Write a lammps input file with minimized configuration for subsequent sims

    L.close()

    return None

# --------------------------- UTILITIES ---------------------------#

def get_dislo_core_ids(filepath, n=None):
    """
    Reads atom IDs from a text file, preserving their order, 
    optionally returning only the first n IDs.

    Parameters:
    -----------
    filepath : str
        Path to the text file containing one ID per line.

    n : int or None, optional
        Number of IDs to return from the start of the file. If None, return all IDs.

    Returns:
    --------
    list of ints
        List of IDs in the order they appear in the file, limited to first n if specified.
    """
    ids = []
    with open(filepath, 'r') as f:
        for line in f:
            if n is not None and len(ids) >= n:
                break
            line = line.strip()
            if line:
                val = float(line)
                if val.is_integer():
                    val = int(val)
                ids.append(int(val))
    return ids

# --------------------------- ENTRY POINT ---------------------------#

if __name__ == "__main__":

    if CLEAR:

        os.makedirs(MASTER_DATA_DIR, exist_ok=True)
        os.makedirs(os.path.join(MASTER_DATA_DIR, MODULE_DIR), exist_ok=True)

        dump_dir = os.path.join(MASTER_DATA_DIR, MODULE_DIR, DUMP_DIR)
        output_dir = os.path.join(MASTER_DATA_DIR, MODULE_DIR, OUTPUT_DIR)

        os.makedirs(dump_dir, exist_ok=True)
        os.makedirs(output_dir, exist_ok=True)

        clear_dir(dump_dir)
        clear_dir(output_dir)

    if MULTIPLE:
        for del_no in ATOMS_TO_DELETE:
            main(del_no)
    else:
        main(ATOMS_TO_DELETE)