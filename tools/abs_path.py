import os

def get_path(called_file):

    # Use the current working directory as the notebook's directory
    notebook_dir = os.getcwd()

    # Construct the path to the called_file
    file_path = os.path.join(notebook_dir, called_file)
    
    return file_path

