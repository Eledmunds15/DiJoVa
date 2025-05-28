import os
import shutil

def set_path():

    filepath = os.path.dirname(os.path.abspath(__file__))
    os.chdir(filepath)

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

