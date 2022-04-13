# DCS Radio Manager

Simple PySide2 GUI application for managing DCS Mission file's 
user-playable module radio presets.

## Installation / Download

Please see the releases section on the right hand side

## Modules

This supports the Avionics `SETTINGS.lua` methods for the A-10C (and _2) 
and F-16C which was the main reason for its creation.

I'll be adding more modules as time permits, but feel free to add them as you see fit

## Help

If you have any trouble, feature requests or other items of interest, please feel free to:

* File an issue on [GitHub](https://github.com/MartinCo/DCSPresetManager/issues)
* Get in touch via [MartinCo#6402](https://discordapp.com/users/219885915198324736) on discord (132nd.MartinCo on [132nd Discord](https://discord.gg/vK2MS2P))
* Get in touch via eMail: [help@dcs-mdc.com](mailto:help@dcs-mdc.com)

## Usage

This also has CLI usage to facilitate CI pipelines 
using either a profile from the profile directory,
or more likely, an explicit preset json that can be
exported from the GUI and live with your mission for
that purpose.

## Thanks

* Feather Icons - Pretty much all the Icons

  * https://feathericons.com/

## Development

* Inkscape (SVG Authoring, Icons, Installer Headers)

  * https://inkscape.org/
  
* Image Magick (PNG -> BMP - for MSI that needs Bitmaps)

  * https://imagemagick.org/index.php

* UPX (Executable Packer for compression)

  * https://upx.github.io/

* Wix Toolset (MSI Build)

  * https://wixtoolset.org/