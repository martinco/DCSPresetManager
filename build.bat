1>2# : ^
'''
@echo off
venv\scripts\python.exe "%~f0"
exit /b
rem ^

This is now python, just made into a nice bat file
'''

import subprocess
import sys
import os
import shutil
import re
import PyInstaller.__main__

from setuptools.sandbox import run_setup

# Application Locations
INKSCAPE = r"C:\Program Files\Inkscape\bin\inkscape.com"
MAGICK = r"C:\Program Files\ImageMagick-7.1.0-Q16-HDRI\magick.exe"
RE_VERSION = re.compile(r'^([0-9]+)(\.[0-9]+){0,3}$')


def cleanup():
    """
    Cleans up build folders
    """
    for x in ['build', 'dist']:
        try:
            shutil.rmtree(x)
        except FileNotFoundError:
            pass


def build_python():
    """
    Builds build/lib/dcs_preset_manager and wheel
    """

    run_setup('setup.py', args=['build'])
    run_setup('setup.py', args=['bdist_wheel'])


def build_exe(version):
    """
    PyInstaller to build our output exes, initial spec was created and merged with the following
    --noconsole, empty, and -F for single file to generate the multiple exe outputs for heat

    pyinstaller.exe ^
      --noconsole ^
      --add-data build\lib\dcs_preset_manager\resources;dcs_preset_manager\resources ^
      -p build\lib ^
      -i build\lib\dcs_preset_manager\resources\icon.ico ^
      -n DCSPresetManager ^
      installer_entry.py
    """

    PyInstaller.__main__.run([
        'DCSPresetManager.spec',
    ])

    # Rename the portable exe to include the version if possible
    if version:
        os.replace(r'dist\DCSPresetManager.exe', r'dist\DCSPresetManager-%s.exe' % version)


def get_version():
    """
    After build, we can import dcs_preset_manager and extract the version.dcs_preset_manager

    MSI installers can only build for x.x.x.x versions, so if we're dirty, bail
    """

    # Add to path so we don't have to, though can't import yet as we need build to happen
    sys.path.append(os.path.join(os.path.dirname(__file__), 'build', 'lib'))
    from dcs_preset_manager import _version  # noqa

    versions = _version.get_versions()
    m = RE_VERSION.match(versions['version'])

    if not m:
        return None

    if versions.get('dirty', False):
        return None

    return versions['version']


def build_msi(version):
    """
    Now we have our PyInstaller output, we can bundle it into an exe
    """

    wix_converts = {
        'WixUIBannerBmp': [493, 58],
        'WixUIDialogBmp': [493, 312],
    }

    try:
        os.makedirs(os.path.join('build', 'wix'))
    except FileExistsError:
        pass

    for prefix, dimensions in wix_converts.items():

        svg = os.path.join('wix', prefix + '.svg')
        png = os.path.join('build', 'wix', prefix + '.png')
        bmp = os.path.join('build', 'wix', prefix + '.bmp')

        # We store our Installer bitmaps as SVGs so use inkscape to build the PNG,
        # And then image magick to convert to BMP for WIX
        if not os.path.exists(bmp):
            subprocess.check_call([INKSCAPE, svg, '-w', str(dimensions[0]), '-h', str(dimensions[1]), '-o', png])
            subprocess.check_call([MAGICK, 'convert', png, bmp])

    wix_env = os.environ.copy()
    wix_env['VERSION'] = version
    wix_bin = os.path.join(os.environ.get('WIX'), 'bin')

    subprocess.call([
        os.path.join(wix_bin, 'heat.exe'), 'dir', r'dist\DCSPresetManager',
        '-ke', '-srd', '-v', '-ag',
        '-cg', 'RootDataGroup',
        '-dr', 'RootData',
        '-t', r'wix\appShortcut.xsl',
        '-out', r'build\wix\src.wix'
    ], env=wix_env)

    print("CANDLE")
    subprocess.call([
        os.path.join(wix_bin, 'candle.exe'),
        '-out', r'build\wix\\',
        r'wix\DCSPresetManager.wxs',
        r'build\wix\src.wix'],
        env=wix_env)

    print("LIGHT")
    subprocess.call([
        os.path.join(wix_bin, 'light.exe'),
        '-ext', 'WixUIExtension',
        '-b', r'dist\DCSPresetManager', r'build\wix\DCSPresetManager.wixobj', r'build\wix\src.wixobj',
        '-pdbout', r'build\wix\DCSPresetManager.pdb',
        '-o', r'dist\DCSPresetManager-%s.msi' % version],
        env=wix_env)


def main():

    cleanup()
    build_python()

    version = get_version()
    build_exe(version)

    if not version:
        print("This project must be tagged correctly to continue to build MSI")
        return 0

    # We don't want to collect our Portable EXE, so move it out the way
    build_msi(version)

if __name__ == '__main__':
    sys.exit(main())
