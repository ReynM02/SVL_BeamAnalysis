@echo off
set venv=EOLTester
set dir=C:\Users\matt.reynolds\OneDrive - Smart Vision Lights\Desktop\SVL_BeamAnalysis\src

call %USERPROFILE%\Anaconda3\Scripts\activate %USERPROFILE%\Anaconda3\envs\%venv%
::call activate %venv%

:: Change directory to the relative path that's needed for script
cd %dir%

:: Run script at this location
call %USERPROFILE%/Anaconda3/envs/%venv%/python.exe "%dir%\GUI.py"
