# --------------------------- LIBRARIES ---------------------------#
import os
from mpi4py import MPI

from ovito.io import import_file, export_file
from ovito.modifiers import TimeAveragingModifier

from utilities import set_path, clear_dir

# --------------------------- CONFIG ---------------------------#

INPUT_DIR = '../05_jog_stability/dump_files_TEST'
INPUT_FILE = 'dumpfile_*'

OUTPUT_DIR = 'processed_files_TEST'

SOMETHING = 5

# --------------------------- ANALYSIS ---------------------------#

def main():
    #--- INITIALISE MPI ---#
    comm = MPI.COMM_WORLD
    rank = comm.Get_rank()
    size = comm.Get_size()

    set_path()

    #--- INITIALISE VARIABLE ON ALL RANKS ---#
    dump_files = None

    #--- CREATE AND SET DIRECTORIES ---#
    if rank == 0:
        os.makedirs(OUTPUT_DIR, exist_ok=True)
        clear_dir(OUTPUT_DIR)

        dump_files = get_filenames(INPUT_DIR)

        print(f"Found {len(dump_files)} dump files to process.")
        print(f"Using {size} ranks for parallel processing.\n")

    #--- BROADCAST AND DISTRIBUTE WORK ---#
    dump_files = comm.bcast(dump_files, root=0)

    print(f"Rank {rank} of size {size} processing {dump_files[:3]}")
    
    comm.Barrier()

    #--- PROCESS FILE ---#

    
    
    return None

# --------------------------- UTILITIES ---------------------------#

def process_files(dump_files):

    output_path = os.path.join(OUTPUT_DIR, dump_files)

    # Load the trajectory (make sure it's multiple frames!)
    pipeline = import_file()

    # Add the time-averaging modifier:
    pipeline.modifiers.append(
        TimeAveragingModifier(
            operate_on = 'property:particles/c_csym',
        )
    )

    # Evaluate at the last frame (you can change this)
    data = pipeline.compute(pipeline.source.num_frames - 1)

    export_file(data, output_path, "lammps/dump",
                columns=["Particle Identifier", "Position.X", "Position.Y", "Position.Z", "c_peratom", "c_csym", "c_csym Average"])

def view_information(data):
    
    print('')
    print("Available particle properties:")
    for prop in data.particles.keys():
        print(f"  - {prop}")

    print("\nAvailable global attributes:")
    for attr in data.attributes.keys():
        print(f"  - {attr}")
    print('')

def get_filenames(dir_path):
    """Returns a naturally sorted list of filenames (not paths) in the given directory."""
    files = [f for f in os.listdir(dir_path) if os.path.isfile(os.path.join(dir_path, f))]
    return sorted(files, key=natural_sort_key)

def natural_sort_key(s):
    # Split the string into digit and non-digit parts, convert digits to int
    return [int(text) if text.isdigit() else text.lower() for text in re.split(r'(\d+)', s)]

def split_files(file_list, rank, size):

    files = []

    for i, dump_file in enumerate(file_list):
        if i % size == rank:
            files.append(dump_file)
            
    return files

# --------------------------- ENTRY POINT ---------------------------#

if __name__ == "__main__":

        main()