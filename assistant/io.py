import os
import glob
from pathlib import Path

def get_directory_structure(path, ignore_files):
    """Generates a string representation of the directory structure."""
    structure = ''
    for root, dirs, files in os.walk(path):
        dirs[:] = [d for d in dirs if os.path.join(root, d) not in ignore_files]
        files = [f for f in files if os.path.join(root, f) not in ignore_files]
        level = root.replace(path, '').count(os.sep)
        indent = ' ' * 4 * (level)
        structure += '{}{}/\n'.format(indent, os.path.basename(root))
        subindent = ' ' * 4 * (level + 1)
        for f in files:
            filepath = os.path.join(root, f)
            structure += '{}{}\n'.format(subindent, f)
            try:
                with open(filepath, 'r') as file:
                    file_content = file.read()
                    structure += f'\n{subindent}## {filepath} ##\n{file_content}\n\n'
            except FileNotFoundError:
                structure += f'\n{subindent}## {filepath} ##\nFile not found\n\n'
            except Exception as e:
                structure += f'\n{subindent}## {filepath} ##\nError reading file: {e}\n\n'
    return structure


def process_assistant_ignore(base_path, ignore_file_path=".assistantignore"):
    """Processes the .assistantignore file."""
    ignore_list = []
    ignore_file = Path(base_path) / ignore_file_path
    if ignore_file.exists():
        with ignore_file.open('r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    pattern = os.path.join(base_path, line)
                    for filepath in glob.glob(pattern):
                        ignore_list.append(filepath)
    else:
        print(f"File {ignore_file} not found. No files will be ignored.")
    return ignore_list


def get_directory_structure_with_ignore(path):
    """Gets the directory structure, applying ignore rules."""
    ignore_files = process_assistant_ignore(path)
    return get_directory_structure(path, ignore_files)

def get_file_content(filepath):
    """Reads the content of a file, returning an empty string if the file doesn't exist."""
    try:
        with open(filepath, 'r') as file:
            return file.read()
    except FileNotFoundError:
        return ""

def create_file(filepath, content=""):
    """Creates a file with the given content."""
    Path(filepath).parent.mkdir(parents=True, exist_ok=True)
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)

def get_latest_file(directory, prefix):
  """Gets the latest file matching a prefix in a directory."""
  files = [f for f in os.listdir(directory) if f.endswith(prefix + '.md')]
  if not files:
      return None
  files.sort(key=lambda x: int(x.split('_')[0].split('.')[0]))
  return files[-1]