SETLOCAL ENABLEDELAYEDEXPANSION
set "output=%1"
set word=_rc.py
set output=%output:.qrc=!word!%
"C:\Python27\Lib\site-packages\PySide\pyside-rcc.exe" -o %output% %1
pause