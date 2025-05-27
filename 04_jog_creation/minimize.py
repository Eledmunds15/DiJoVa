# --------------------------- LIBRARIES ---------------------------#
import os
from mpi4py import MPI
from lammps import lammps, PyLammps

# --------------------------- CONFIG ---------------------------#

INPUT_DIR = '../02_minimize_dislo/min_input'
INPUT_FILE = 'straight_edge_dislo.lmp'

DISLO_CORE_IDS_DIR = '../03_dislo_analysis'
DISLO_CORE_IDS_FILE = 'deleted_ids.txt'
ATOMS_TO_DELETE = [1, 60] # Takes a list of integer values which determine the number of atoms it will delete.

DUMP_DIR = 'min_dump'
OUTPUT_DIR = 'min_input'

POTENTIAL_DIR = '../00_potentials'
POTENTIAL_FILE = 'malerba.fs'

ENERGY_TOL = 1e-8
FORCE_TOL = 1e-10

# --------------------------- MINIMIZATION ---------------------------#

def main(atoms_to_delete):

    #--- Initialise MPI ---#
    comm = MPI.COMM_WORLD
    rank = comm.Get_rank()
    size = comm.Get_size()

    if rank == 0: print(f"Minimizing structure after deletion of {i} atoms")

    #--- Create and set directories ---#

    input_filepath = os.path.join(INPUT_DIR, INPUT_FILE)

    output_file = f'edge_dislo_{atoms_to_delete}.lmp'
    dump_file = f'edge_dislo_{atoms_to_delete}_dump'

    output_filepath = os.path.join(OUTPUT_DIR, output_file)
    dump_filepath = os.path.join(DUMP_DIR, dump_file)

    potential_path = os.path.join(POTENTIAL_DIR, POTENTIAL_FILE)
    dislo_ids_path = os.path.join(DISLO_CORE_IDS_DIR, DISLO_CORE_IDS_FILE)

    #--- GET DISLOCATION CORE IDS ---#
    dis_core_ids = get_dislo_core_ids(dislo_ids_path, atoms_to_delete)

    #--- LAMMPS SCRIPT ---#
    lmp = lammps()
    L = PyLammps(ptr=lmp)

    L.units('metal') # Set units style
    L.atom_style('atomic') # Set atom style

    L.command('boundary f f p') # Set the boundaries of the simulation

    L.read_data(input_filepath) # Read input file

    L.pair_style('eam/fs') # Set the potential style
    L.pair_coeff('*', '*', potential_path, 'Fe') # Select the potential

    L.group('fe_atoms', 'type', 1) # Group all atoms

    id_str = ' '.join(str(id) for id in dis_core_ids)
    L.group('del_atoms', 'id', id_str)
    L.delete_atoms('group', 'del_atoms')

    L.compute('peratom', 'all', 'pe/atom') # Set a compute to track the peratom energy

    L.minimize(ENERGY_TOL, FORCE_TOL, 1000, 10000) # Execute minimization

    L.write_dump('all', 'custom', dump_filepath, 'id', 'x', 'y', 'z', 'c_peratom') # Write a dumpfile containing atom positions and pot energies
    L.write_data(output_filepath) # Write a lammps input file with minimized configuration for subsequent sims

    L.close()

    return None

# --------------------------- UTILITIES ---------------------------#

def set_path():

    filepath = os.path.dirname(os.path.abspath(__file__))
    os.chdir(filepath)
    # print(f'Working directory set to: {filepath}')

def clear_dir(dir_path):
     
    if not os.path.isdir(dir_path):
        raise ValueError(f"The path '{dir_path}' is not a directory or does not exist.")
    
    for filename in os.listdir(dir_path):
        file_path = os.path.join(dir_path, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)  # remove file or symlink
            elif os.path.isdir(file_path):
                # Optional: if you want to delete subdirectories too
                for root, dirs, files in os.walk(file_path, topdown=False):
                    for f in files:
                        os.unlink(os.path.join(root, f))
                    for d in dirs:
                        os.rmdir(os.path.join(root, d))
                os.rmdir(file_path)
        except Exception as e:
            print(f"Failed to delete {file_path}. Reason: {e}")

def initialize_directories():

    set_path() # Set path to location of current directory

    os.makedirs(DUMP_DIR, exist_ok=True) # Create the dump directory
    os.makedirs(OUTPUT_DIR, exist_ok=True) # Create the output directory

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

    initialize_directories()

    if len(ATOMS_TO_DELETE) < 1:
        raise ValueError("ATOMS_TO_DELETE is empty. Please add parameters")

    for i in ATOMS_TO_DELETE:
        main(i)