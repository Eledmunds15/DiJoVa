import os
import sys
import shutil

def set_path():
    # This gets the file path of the script that was executed
    script_path = os.path.abspath(sys.argv[0])
    script_dir = os.path.dirname(script_path)
    os.chdir(script_dir)
    print(f"[DEBUG] Working directory set to: {script_dir}")

def del_file(filepath):
    full_path = os.path.abspath(filepath)
    print(f"[DEBUG] Checking for file: {full_path}")
    
    if not os.path.exists(full_path):
        raise FileNotFoundError(f"The file '{filepath}' does not exist.")
    
    os.remove(full_path)
    print(f"[INFO] Deleted file: {full_path}")

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

