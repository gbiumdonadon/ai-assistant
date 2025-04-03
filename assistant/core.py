# -*- coding: utf-8 -*-
import os

def get_next_file_number(directory, prefix):
    """Gets the next available file number for a given prefix."""
    files = [f for f in os.listdir(directory) if f.endswith(prefix + '.md')]
    if not files:
        return 1
    numbers = [int(f.split('_')[0].split('.')[0]) for f in files]
    return max(numbers) + 1

def process_assistant_response(response_json):
    """Safely extracts generated text from the API response."""
    try:
        return response_json['candidates'][0]['content']['parts'][0]['text']
    except (KeyError, IndexError) as e:
        raise ValueError(f"Could not process API response: {e}") from e