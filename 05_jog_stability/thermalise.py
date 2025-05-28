# --------------------------- LIBRARIES ---------------------------#
import os
import numpy as np
from mpi4py import MPI
from lammps import lammps, PyLammps

from utilities import set_path, clear_dir

# --------------------------- CONFIG ---------------------------#

INPUT_DIR = '../04_jog_creation/min_input'
INPUT_FILE = 'edge_dislo_1.lmp'

DUMP_DIR = 'dump_files'

POTENTIAL_DIR = '../00_potentials'
POTENTIAL_FILE = 'malerba.fs'

TEMPERATURE = 600

DIS_CORE_RADIUS = 25
FIXED_REGION_LENGTH = 10

DT = 0.001
DUMP_FREQ = 1000
RUN_TIME = 100

# --------------------------- MINIMIZATION ---------------------------#

def main():

    #--- INITIALISE MPI ---#
    comm = MPI.COMM_WORLD
    rank = comm.Get_rank()
    size = comm.Get_size()

    set_path()

    #--- CREATE AND SET DIRECTORIES ---#
    if rank == 0: 
        os.makedirs(DUMP_DIR, exist_ok=True)
        clear_dir(DUMP_DIR)

    input_filepath = os.path.join(INPUT_DIR, INPUT_FILE)

    dump_file = f'dumpfile_*'

    dump_filepath = os.path.join(DUMP_DIR, dump_file)

    potential_path = os.path.join(POTENTIAL_DIR, POTENTIAL_FILE)

    #--- LAMMPS SCRIPT ---#
    lmp = lammps()
    L = PyLammps(ptr=lmp)

    #--- SETTINGS ---#
    L.units('metal') # Set units style
    L.atom_style('atomic') # Set atom style

    L.command('boundary f f p') # Set the boundaries of the simulation

    L.read_data(input_filepath) # Read input file

    L.pair_style('eam/fs') # Set the potential style
    L.pair_coeff('*', '*', potential_path, 'Fe') # Select the potential

    #--- GET BOX BOUNDS ---#
    box_bounds = lmp.extract_box()

    box_min = box_bounds[0]
    box_max = box_bounds[1]

    xmin, xmax = box_min[0], box_max[0]
    ymin, ymax = box_min[1], box_max[1]
    zmin, zmax = box_min[2], box_max[2]

    sim_box_center = [np.mean([xmin, xmax]), np.mean([ymin, ymax]), np.mean([zmin, zmax])]

    xmid = (xmin+xmax)/2
    ymid = (ymin+ymax)/2

    cyl_radius = min([((xmax-xmin)/2), (ymax-ymin)/2])
    mobile_atoms_radius = cyl_radius-FIXED_REGION_LENGTH

    #--- DEFINE REGIONS ---#
    L.region('dis_region', 'cylinder', 'z', xmid, ymid, DIS_CORE_RADIUS, 'INF', 'INF')
    L.region('mobile_region', 'cylinder', 'z', xmid, ymid, mobile_atoms_radius, 'INF', 'INF')

    #--- GROUP ATOMS ---#
    L.group('fe_atoms', 'type', 1) # Group all atoms
    L.group('dis_core', 'region', 'dis_region')
    L.group('mobile', 'region', 'mobile_region')
    L.group('fixed', 'subtract', 'all', 'mobile')
    
    #--- DEFINE COMPUTES ---#
    L.compute('csym', 'all', 'centro/atom', 'bcc')
    L.compute('peratom', 'all', 'pe/atom') # Set a compute to track the peratom energy

    #--- DEFINE FIXES AND VELOCITIES ---#

    L.fix('1', 'all', 'nvt', 'temp', TEMPERATURE, TEMPERATURE, 100.0*DT)

    L.velocity('mobile', 'create', TEMPERATURE, 43123, 'mom', 'yes', 'rot', 'yes')

    L.fix('boundary_freeze', 'fixed', 'setforce', 0.0, 0.0, 0.0)
    L.velocity('fixed', 'set', 0.0, 0.0, 0.0)

    #--- DEFINE THERMO ---#

    L.thermo_style('custom', 'step', 'temp', 'pe', 'etotal')
    L.thermo(1000)

    #--- DEFINE DUMP ---#
    L.dump('1', 'dis_core', 'custom', DUMP_FREQ, dump_filepath, 'id', 'x', 'y', 'z', 'c_peratom', 'c_csym')

    L.run(RUN_TIME)

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

    main()