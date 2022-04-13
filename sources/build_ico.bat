@ECHO OFF

SET INKSCAPE="C:\Program Files\Inkscape\bin\inkscape.com"
SET MAGICK="C:\Program Files\ImageMagick-7.1.0-Q16-HDRI\magick.exe"


mkdir build > nul

%INKSCAPE% icon.svg -w 16 -h 16 -o build\16.png
%INKSCAPE% icon.svg -w 32 -h 32 -o build\32.png
%INKSCAPE% icon.svg -w 48 -h 48 -o build\48.png
%INKSCAPE% icon.svg -w 64 -h 64 -o build\64.png

%MAGICK% convert build\16.png build\32.png build\48.png build\64.png icon.ico

pause