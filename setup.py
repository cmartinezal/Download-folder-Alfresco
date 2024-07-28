from setuptools import setup, find_packages
from pathlib import Path
this_directory = Path(__file__).parent
readme = (this_directory / 'README.md').read_text()
license = (this_directory / 'LICENSE').read_text()

setup(
    name='download_folder_Alfresco',
    version='1.0',
    license=license,
    description='Project to download a folder from Alfresco using CMIS and REST API.',
    long_description=readme,
    author='Carolina Martinez',
    packages=find_packages(),
)
