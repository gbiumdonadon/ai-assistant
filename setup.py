import os
from setuptools import setup, find_packages

# Determine the current directory to handle relative paths robustly
current_dir = os.path.abspath(os.path.dirname(__file__))

# Read the long description from README.md if it exists
try:
    with open(os.path.join(current_dir, 'README.md'), encoding='utf-8') as f:
        long_description = f.read()
except FileNotFoundError:
    long_description = "Assistant package"

setup(
    name='ai_assistant',
    version='0.1.0',
    packages=find_packages(),  # Use find_packages() to automatically detect packages, but ensure __init__.py exists in assistant directory.
    install_requires=[
        'requests',
        'google-api-core',
        'python-dotenv'
    ],
    entry_points={
        'console_scripts': [
            'ai_assistant = assistant.main:main',
        ],
    },
    long_description=long_description,
    long_description_content_type='text/markdown', # For README.md rendering
    author="Gustavo Bium Donadon",
    url="https://github.com/yourusername/assistant", # Add your repo url here
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License", # Add your license here
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.7', # Specify minimum python version
)