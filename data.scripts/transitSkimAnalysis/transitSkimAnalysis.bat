@echo off
TITLE MTC Transit Skim Analysis
color 70
cls

echo *********************************************************************
echo *  MTC TRANSIT SKIM SET ANALYSIS                                    * 
echo *  @author: sn (narayanamoorthys@pbworld.com)                       *                  
echo *********************************************************************
echo.
@echo off
SETLOCAL ENABLEEXTENSIONS
SETLOCAL ENABLEDELAYEDEXPANSION
rem Setting up directory paths
set WORKINGDIR=%CD%
set PYTHONPATH=C:\Python27-64
set DIR1=skims_raw
set DIR2=skims

rem Exporting unedited skims to csv files
ROBOCOPY %WORKINGDIR% %WORKINGDIR%/%DIR1% ExportTransitSetToCSV.job
cd %DIR1%
IF NOT EXIST csv MD csv
runtpp %WORKINGDIR%\%DIR1%\ExportTransitSetToCSV.job
IF ERRORLEVEL 2 GOTO throwerror
cd ..

rem Exporting edited skims to csv files
ROBOCOPY %WORKINGDIR% %WORKINGDIR%/%DIR2% ExportTransitSetToCSV.job
cd %DIR2%
IF NOT EXIST csv MD csv
runtpp %WORKINGDIR%\%DIR2%\ExportTransitSetToCSV.job
IF ERRORLEVEL 2 GOTO throwerror
cd ..

GOTO :fine

:throwerror
echo Something went wrong!
GOTO end

:fine
echo 
echo "Analysis complete! Results in reports folder!"
ENDLOCAL
exit /B
