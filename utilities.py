import os
import sys
import re
import shutil

def set_path(path=None):
    """
    Set the current working directory.

    If a path is provided, set the working directory to that path.
    If no path is provided, set it to the directory of the running script.
    """
    if path:
        abs_path = os.path.abspath(path)
    else:
        abs_path = os.path.dirname(os.path.abspath(sys.argv[0]))
    
    os.chdir(abs_path)
    # Uncomment below to debug the working directory being set
    # print(f"[DEBUG] Working directory set to: {abs_path}")

def del_file(filepath):
    """
    Delete a file if it exists.
    
    Parameters:
    ----------
    filepath : str
        Path to the file to be deleted. Can be relative or absolute.
        
    Raises:
    -------
    FileNotFoundError:
        If the file does not exist at the specified path.
    """
    full_path = os.path.abspath(filepath)
    # Uncomment below to debug file path check
    # print(f"[DEBUG] Checking for file: {full_path}")

    if not os.path.exists(full_path):
        raise FileNotFoundError(f"The file '{filepath}' does not exist.")
    
    os.remove(full_path)
    # Uncomment below to confirm deletion
    # print(f"[INFO] Deleted file: {full_path}")


def clear_dir(dir_path):
    """
    Remove all files and subdirectories inside the specified directory.
    
    Parameters:
    ----------
    dir_path : str
        Path to the directory to clear.
        
    Raises:
    -------
    ValueError:
        If the given path is not a directory or does not exist.
    """
    if not os.path.isdir(dir_path):
        raise ValueError(f"The path '{dir_path}' is not a directory or does not exist.")
    
    for entry in os.listdir(dir_path):
        entry_path = os.path.join(dir_path, entry)
        try:
            if os.path.isfile(entry_path) or os.path.islink(entry_path):
                os.unlink(entry_path)  # Remove file or symbolic link
            elif os.path.isdir(entry_path):
                shutil.rmtree(entry_path)  # Remove directory and all contents
        except Exception as e:
            print(f"[ERROR] Failed to delete '{entry_path}'. Reason: {e}")