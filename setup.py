from setuptools import setup, find_packages

setup(
    name='tools',
    version='0.1',
    packages=find_packages(),
    description='Tools to help with calcs',
    package_data={'tools.data': ['*.csv'], },  # Include CSV files from the data directory
    include_package_data=True,
    install_requires=[
        'pandas',  # Add 'pandas' to your install requires if your package depends on it
    ],
)
