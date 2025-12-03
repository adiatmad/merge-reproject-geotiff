# GeoTIFF Merger & Reprojector Tool

## 📋 Overview

A powerful, user-friendly Python tool for merging and reprojecting GeoTIFF files with live logging and interactive selection based on this scripts : https://gist.github.com/SColchester/525e24dac4e67c3bd282b4c4ebbcddc1

## ✨ Features

- **Merge Multiple GeoTIFFs**: Combine multiple geospatial raster files into a single mosaic
- **Reproject Images**: Convert between coordinate systems (WGS84, UTM, custom EPSG codes)
- **Interactive File Selection**: Choose files visually with detailed file information
- **Live Progress Logging**: Real-time updates during processing
- **Multiple Processing Modes**: 
  - Merge only
  - Reproject only  
  - Merge and reproject
- **Automatic CRS Detection**: Smart UTM zone selection based on image location
- **Preserves Metadata**: Maintains geospatial information and data integrity

## 🚀 Quick Start

### Prerequisites
- Python 3.7 or higher
- Windows, macOS, or Linux

### Installation

#### Option 1: One-Click Install (Windows)
1. Place both `install.bat` and `merge_tool.py` in your folder with GeoTIFF files
2. Double-click `install.bat`
3. The tool will automatically install dependencies and launch

#### Option 2: Manual Installation
```bash
# Install required packages
pip install rasterio numpy

# Or with pip3
pip3 install rasterio numpy

# Run the tool
python merge_tool.py
```

## 📖 How to Use

### Step-by-Step Guide

1. **Prepare Your Files**
   - Place all GeoTIFF files (.tif, .tiff, .geotiff) in the same folder as the tool
   - Ensure files have geospatial metadata (coordinates)

2. **Launch the Tool**
   - Run `install.bat` (Windows) or `python merge_tool.py` (all platforms)

3. **Select Files**
   - View all available GeoTIFFs with size and dimension information
   - Choose files:
     - `A` for all files
     - Enter numbers (e.g., `1,3,5` or `1-3`)
     - `Q` to quit

4. **Choose Processing Mode**
   - **Mode 1**: Merge Only - Combine files without changing coordinate system
   - **Mode 2**: Reproject Only - Change coordinate system of a single file
   - **Mode 3**: Merge AND Reproject - Combine files and convert to new CRS (recommended)

5. **Select Coordinate System** (for modes 2 & 3)
   - **Option 1**: WGS84 (EPSG:4326) - For web maps, Google Earth
   - **Option 2**: UTM Zone - Automatic selection based on image location
   - **Option 3**: Custom EPSG code (e.g., 3857 for Web Mercator)
   - **Option 4**: Keep original CRS

6. **Set Output Name**
   - Enter filename or press Enter for default
   - Confirm overwrite if file exists

7. **Monitor Processing**
   - Watch live logs for real-time progress
   - See file sizes, transformations, and any warnings

8. **View Results**
   - Get detailed output file information
   - See processing time statistics

## 🗂️ Supported File Formats

- **GeoTIFF** (.tif, .tiff, .geotiff)
- **Multi-band raster files**
- **Various data types** (Float32, UInt16, etc.)

## 🌐 Supported Coordinate Systems

- **WGS84** (EPSG:4326)
- **UTM** All zones (automatic detection)
- **Web Mercator** (EPSG:3857)
- **Any EPSG-coded system**
- **Original CRS preservation**

## ⚙️ Advanced Options

### Command Line Arguments
Currently, the tool runs in interactive mode only. For batch processing, modify the script directly.

### Custom EPSG Codes
Common EPSG codes:
- `4326`: WGS84 (latitude/longitude)
- `3857`: Web Mercator (Google Maps, OpenStreetMap)
- `32633`: UTM Zone 33N (Central Europe)
- `32733`: UTM Zone 33S

### Processing Settings
- **Resampling**: Bilinear interpolation (configurable in code)
- **Compression**: DEFLATE compression for smaller file sizes
- **Tiling**: Enabled for large files (faster access)

## 🛠️ Troubleshooting

### Common Issues

1. **"No GeoTIFF files found"**
   - Ensure files have .tif/.tiff extension
   - Check file is a valid GeoTIFF with spatial reference

2. **"Cannot read file"**
   - File might be corrupted or lack geospatial metadata
   - Try opening in QGIS or GDAL first

3. **Installation fails**
   - Install GDAL separately on some systems: `pip install GDAL`
   - Use Conda: `conda install -c conda-forge rasterio`

4. **Memory errors with large files**
   - Process fewer files at once
   - Increase system RAM
   - Use `--co BLOCKXSIZE=512 --co BLOCKYSIZE=512` in output options

### Performance Tips

- **For large datasets**: Process in batches
- **Disk space**: Ensure 2-3x free space of input files
- **RAM**: At least 8GB recommended for large mosaics

## 📊 Output Information

The tool provides comprehensive output details:
- File size and dimensions
- Coordinate reference system
- Band count and data type
- Sample statistics
- Processing time

## 🔧 Development

### File Structure
- `install.bat`: Windows installer script
- `merge_tool.py`: Main Python application

### Dependencies
- `rasterio`: Geospatial raster I/O
- `numpy`: Numerical processing
- Built-in: `os`, `sys`, `time`, `threading`, `queue`

### Extending the Tool
To add features:
1. New processing modes: Add to `get_processing_mode()`
2. Additional CRS options: Modify `get_crs_choice()`
3. Custom resampling: Change `Resampling.bilinear` to other methods

## 📄 License

Open-source tool for geospatial processing. Modify and distribute as needed.

## 🤝 Support

For issues or feature requests:
1. Check troubleshooting section
2. Ensure packages are updated: `pip install --upgrade rasterio`
3. Verify file integrity with other GIS software

## ⏱️ Processing Time Estimates

- Small files (<100MB): 1-5 minutes
- Medium files (100MB-1GB): 5-20 minutes  
- Large files (>1GB): 20+ minutes (monitor memory usage)

---

**Happy mapping!** 🗺️
