# --------------------------- LIBRARIES ---------------------------#
import os
from mpi4py import MPI

from ovito.io import import_file, export_file
from ovito.modifiers import TimeAveragingModifier

from utilities import set_path, clear_dir, get_filenames, split_files

# --------------------------- CONFIG ---------------------------#

INPUT_DIR = '../05_jog_stability/dump_files_TEST'
INPUT_FILE = 'dumpfile_*'

OUTPUT_DIR = 'processed_files'

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
    dump_files_rank = split_files(dump_files, rank, size)

    print(f"Rank {rank} of size {size} processing {dump_files_rank[:3]}")
    
    comm.Barrier()

    #--- VIEW INFORMATION ---#

    if rank == 0: view_information(dump_files[0])

    #--- PROCESS FILE ---#

    for file in dump_files_rank:
         process_file(file)

    return None

# --------------------------- UTILITIES ---------------------------#


def process_file(dump_file):
    input_path = os.path.join(INPUT_DIR, dump_file)
    output_path = os.path.join(OUTPUT_DIR, dump_file)

    # Load the trajectory (make sure it's multiple frames!)
    pipeline = import_file(input_path)

    # Add the time-averaging modifier:
    pipeline.modifiers.append(
        TimeAveragingModifier(
            operate_on = 'property:particles/c_csym',
            sampling_frequency = 5,
        )
    )

    # Evaluate at the last frame (you can change this)
    data = pipeline.compute(pipeline.source.num_frames - 1)

def view_information(dump_file):
     
    input_path = os.path.join(INPUT_DIR, dump_file)

    pipeline = import_file(input_path)

    data = pipeline.compute(pipeline.source.num_frames - 1)
    
    print('')
    print("Available particle properties:")
    for prop in data.particles.keys():
        print(f"  - {prop}")

    print("\nAvailable global attributes:")
    for attr in data.attributes.keys():
        print(f"  - {attr}")
    print('')

# --------------------------- ENTRY POINT ---------------------------#

if __name__ == "__main__":

        main()