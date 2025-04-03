from setuptools import setup, find_packages

setup(
    name='assistant',  # Replace with your package name
    version='0.1.0',
    packages=find_packages(),
    install_requires=[  # List any dependencies here
        #e.g., "requests",
    ],
    entry_points={
        'console_scripts': [
            'ai_assistant = assistant.main:main',  # Replace main with the actual module name if different.
        ],
    },
)