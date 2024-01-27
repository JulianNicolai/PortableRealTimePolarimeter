@echo off
if "%~1"=="" (
echo Function name not provided.
) else (
set directory=%1
mkdir "%directory%"
cd "%directory%"
echo Made %directory% directory.
echo Building Python virtual env...
python -m venv .venv
.\.venv\Scripts\activate.bat
echo Initialising maturin...
maturin init
echo Developing maturin...
maturin develop
)