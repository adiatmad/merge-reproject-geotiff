@echo off
echo ========================================
echo    GEOTIFF MERGER & REPROJECTOR
echo ========================================
echo.
echo Installing required packages...
echo.

pip install rasterio numpy --quiet
if %errorlevel% neq 0 (
    echo Trying with pip3...
    pip3 install rasterio numpy --quiet
)

echo.
echo ✅ Installation complete!
echo.
echo Running merger tool...
echo ========================================
echo.
python merge_tool.py
pause