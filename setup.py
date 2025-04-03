from setuptools import setup, find_packages

setup(
    name='assistant',
    version='0.1.0',
    packages=find_packages(),
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
)