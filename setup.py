import os
import sys
import versioneer

from setuptools import setup, find_packages

with open('readme.md') as f:
    readme = f.read()

setup(
    name='dcs-preset-manager',
    version=versioneer.get_version(),
    cmdclass=versioneer.get_cmdclass(),
    description='Manages DCS Mission file client module radio presets',
    long_description=readme,
    author='Martin Collins',
    author_email='martin@hatchlane.com',
    url='https://github.com/MartinCo/dcs_preset_manager',
    license="MIT",
    package_dir={"": "src"},
    packages=find_packages("./src"),
    package_data={'dcs_preset_manager': ['resources/**']},
    include_package_data=True,
    install_requires=[
        'PySide2',
        'six',
    ],
    entry_points={
        'console_scripts': [
            'dcs-preset-manager = dcs_preset_manager.app:main',
        ],
    },
)