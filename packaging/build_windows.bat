@echo off
REM ---------------------------------------------------------------
REM Build ThermalDesignAgent.exe on Windows.
REM
REM Requirements: Python 3.12 (64-bit) available as "py -3.12".
REM Optional:     Inno Setup 6 (iscc on PATH) to build the installer.
REM
REM Output:
REM   dist\ThermalDesignAgent\ThermalDesignAgent.exe
REM   dist\ThermalDesignAgent-2.0.0-win64.zip
REM   dist\ThermalDesignAgent-2.0.0-setup.exe   (if Inno Setup found)
REM ---------------------------------------------------------------

setlocal
cd /d "%~dp0.."

if not exist build-venv (
    py -3.12 -m venv build-venv 2>nul || python -m venv build-venv || goto :error
)

call build-venv\Scripts\activate.bat || goto :error

python -m pip install --upgrade pip || goto :error
python -m pip install -r packaging\requirements-build.txt || goto :error

pyinstaller --noconfirm --clean packaging\ThermalDesignAgent.spec || goto :error

copy /y packaging\.env.example dist\ThermalDesignAgent\.env.example >nul

echo.
echo Running self-test...
set LLM_PROVIDER=mock
dist\ThermalDesignAgent\ThermalDesignAgent.exe --selftest || goto :error
set LLM_PROVIDER=

powershell -NoProfile -Command "Compress-Archive -Force -Path dist\ThermalDesignAgent -DestinationPath dist\ThermalDesignAgent-2.0.0-win64.zip" || goto :error

where iscc >nul 2>nul
if %errorlevel%==0 (
    iscc packaging\installer.iss || goto :error
) else (
    echo Inno Setup not found - skipping installer. Zip is ready.
)

echo.
echo BUILD OK
dir /b dist
exit /b 0

:error
echo.
echo BUILD FAILED
exit /b 1
