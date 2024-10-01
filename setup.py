import os
import platform
from setuptools import setup, find_packages
import subprocess
import sys
import site
from distutils.sysconfig import get_python_lib
python_path = sys.executable
#package_path = site.getsitepackages()
package_path = get_python_lib()

# Get the platform name and set different library file name
platform_name = platform.system()
if platform_name == 'Linux':
    desktop_path = os.path.join(os.path.join(os.path.expanduser('~')), 'Desktop')
    if os.path.isdir('desktop_path') == False:
        desktop_path = os.path.join(os.path.expanduser('~'))
    f = open(os.path.join(desktop_path, 'leapctrails.sh'), "w")
    f.write('#!/bin/sh\n')
    f.write('python ' + str(os.path.join(package_path, 'leapctrails', 'launch_leapctrails.py')) + '\n')
    f.close()
    os.chmod(os.path.join(desktop_path, 'leapctrails.sh'), 0o755)
elif platform_name == 'Windows':
    desktop_path = os.path.join(os.path.join(os.environ['USERPROFILE']), 'Desktop')
    f = open(os.path.join(desktop_path, 'leapctrails.bat'), "w")
    f.write(python_path + ' ' + str(os.path.join(package_path, 'leapctrails', 'launch_leapctrails.py')) + '\n')
    f.write('pause\n')
    f.close()
else:
    raise Exception(f'{platform_name} is not supported.')



setup(
    name='leapctrails',
    version='0.3',
    author='Kyle Champley',
    author_email="champley@gmail.com",
    description='PyQt GUI for LEAP-CT',
    url="https://github.com/kylechampley/LEAPCT-UI-GUI",
    packages=find_packages(),
    include_package_data=True,
    #package_data={'leapctrails': ['ZiteoIcon.png', lib_file, 'data/XCOM/*', 'data/EPDL/*']},
    platforms=[platform_name],
    install_requires=[
        'matplotlib',
        'numpy',
        'scipy',
        'napari',
        'imageio',
        'PyQt5',
    ],
    python_requires='>=3.10',
    license_files=('LICENSE.txt'),
)
