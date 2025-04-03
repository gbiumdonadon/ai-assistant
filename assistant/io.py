# -*- coding: utf-8 -*-
import os
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def get_directory_structure(path, ignore_files):
    """Generates a string representation of the directory structure."""
    structure = ''
    for root, dirs, files in os.walk(path):
        # Filter out directories to ignore
        dirs[:] = [d for d in dirs if os.path.abspath(os.path.join(root, d)) not in ignore_files]
        # Filter out files to ignore
        files = [f for f in files if os.path.abspath(os.path.join(root, f)) not in ignore_files]
        level = root.replace(path, '').count(os.sep)
        indent = ' ' * 4 * (level)
        structure += '{}{}/\n'.format(indent, os.path.basename(root))
        subindent = ' ' * 4 * (level + 1)
        for f in files:
            filepath = os.path.join(root, f)
            structure += '{}{}\n'.format(subindent, f)
            try:
                with open(filepath, 'r', encoding='utf-8') as file:
                    file_content = file.read()
                    structure += f'\n{subindent}################ filepath: `{filepath}` ################\n{file_content}\n\n'
            except FileNotFoundError:
                logging.warning(f"File not found: {filepath}")
            except Exception as e:
                logging.warning(f"Error reading file {filepath}: {e}")
    return structure


def process_assistant_ignore(base_path, ignore_file_path=".assistantignore"):
    """Processes the .assistantignore file, handling relative and absolute paths correctly."""
    ignore_list = set()
    ignore_file = Path(base_path) / ignore_file_path
    if ignore_file.exists():
        logging.info(f"Processing ignore file: {ignore_file}")
        try:
            with ignore_file.open('r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        # Construct the absolute path of the ignore pattern
                        ignore_path = os.path.abspath(os.path.join(base_path, line))
                        logging.debug(f"Ignore pattern (absolute): {ignore_path}")
                        ignore_list.add(ignore_path)
                        # If it's a directory, ensure all its contents are also ignored
                        if os.path.isdir(ignore_path):
                            for root, dirs, files in os.walk(ignore_path):
                                for name in dirs:
                                    ignore_list.add(os.path.abspath(os.path.join(root, name)))
                                for name in files:
                                    ignore_list.add(os.path.abspath(os.path.join(root, name)))

        except Exception as e:
            logging.error(f"Error reading .assistantignore file: {e}")
    else:
        logging.info(f"File {ignore_file} not found. No files will be ignored.")
    return ignore_list

def get_directory_structure_with_ignore(path):
    """Gets the directory structure, applying ignore rules."""
    ignore_files = process_assistant_ignore(path)
    logging.info(f"Files and directories to ignore: {ignore_files}")
    return get_directory_structure(path, ignore_files)

def get_file_content(filepath):
    """Reads the content of a file, returning an empty string if the file doesn't exist."""
    try:
        with open(filepath, 'r') as file:
            return file.read()
    except FileNotFoundError:
        logging.warning(f"File not found: {filepath}")
        return ""
    except Exception as e:
        logging.error(f"Error reading file {filepath}: {e}")
        return ""

def create_file(filepath, content=""):
    """Creates a file with the given content."""
    Path(filepath).parent.mkdir(parents=True, exist_ok=True)
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        logging.info(f"File created: {filepath}")
    except Exception as e:
        logging.error(f"Error creating file {filepath}: {e}")

def get_latest_file(directory, prefix):
  """Gets the latest file matching a prefix in a directory."""
  files = [f for f in os.listdir(directory) if f.endswith(prefix + '.md')]
  if not files:
      return None
  files.sort(key=lambda x: int(x.split('_')[0].split('.')[0]))
  latest_file = files[-1]
  logging.info(f"Latest file found: {latest_file}")
  return latest_file