# merge_tool.py - Enhanced with live logging and all options
import os
import sys
import time
from datetime import datetime
import threading
import queue

# Try to import, install if missing
try:
    import rasterio
    from rasterio.merge import merge
    from rasterio.warp import calculate_default_transform, reproject, Resampling
    import numpy as np
    PRINT_READY = True
except ImportError:
    print("Installing missing packages...")
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "rasterio", "numpy"])
    print("\n✅ Packages installed! Please run the script again.")
    input("\nPress Enter to exit...")
    sys.exit()

# ==================== LOGGING SYSTEM ====================
class LiveLogger:
    def __init__(self):
        self.log_queue = queue.Queue()
        self.running = True
        self.last_update = time.time()
        
    def log(self, message, level="INFO"):
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] {message}"
        self.log_queue.put(log_entry)
        
    def get_logs(self):
        logs = []
        while not self.log_queue.empty():
            logs.append(self.log_queue.get())
        return logs
    
    def stop(self):
        self.running = False

logger = LiveLogger()

def print_logs_continuously():
    """Background thread to print logs"""
    while logger.running:
        logs = logger.get_logs()
        for log in logs:
            print(f"  {log}")
        time.sleep(0.1)

# Start logging thread
log_thread = threading.Thread(target=print_logs_continuously, daemon=True)
log_thread.start()

# ==================== MAIN TOOL ====================
def clear_screen():
    """Clear console screen"""
    os.system('cls' if os.name == 'nt' else 'clear')

def print_header():
    """Print tool header"""
    clear_screen()
    print("=" * 60)
    print("           🌍 GEOTIFF PROCESSING TOOL")
    print("=" * 60)
    print("✅ Live logging enabled - See progress below")
    print("-" * 60)

def find_tif_files():
    """Find all GeoTIFF files in current directory"""
    tif_files = []
    for f in os.listdir('.'):
        if f.lower().endswith(('.tif', '.tiff', '.geotiff')):
            tif_files.append(f)
    return sorted(tif_files)

def select_files_interactive(tif_files):
    """Let user select files interactively"""
    print_header()
    print("\n📁 FILES IN CURRENT FOLDER:\n")
    
    for i, f in enumerate(tif_files, 1):
        try:
            with rasterio.open(f) as src:
                size_mb = os.path.getsize(f) / 1024 / 1024
                print(f"{i:2}. {f[:40]:40} | {size_mb:5.1f} MB | {src.width:5d}×{src.height:<5d} | {src.crs or 'No CRS':10}")
        except:
            print(f"{i:2}. {f[:40]:40} | (Cannot read)")
    
    print("\n" + "-" * 60)
    print("SELECT FILES TO PROCESS:")
    print("  [A] - ALL files")
    print("  [N] - Enter numbers (e.g., 1,3,5 or 1-3)")
    print("  [Q] - Quit")
    
    choice = input("\nYour choice: ").upper().strip()
    
    if choice == 'Q':
        return None
    elif choice == 'A':
        return tif_files
    else:
        try:
            selected = []
            for part in choice.split(','):
                part = part.strip()
                if '-' in part:
                    start, end = map(int, part.split('-'))
                    selected.extend(range(start, end + 1))
                else:
                    selected.append(int(part))
            
            # Convert to file names
            selected_files = []
            for num in selected:
                if 1 <= num <= len(tif_files):
                    selected_files.append(tif_files[num-1])
                else:
                    logger.log(f"Warning: File #{num} doesn't exist", "WARN")
            
            return selected_files if selected_files else tif_files
        except:
            logger.log("Invalid selection, using ALL files", "WARN")
            return tif_files

def get_processing_mode():
    """Let user choose processing mode"""
    print_header()
    print("\n🛠️  SELECT PROCESSING MODE:\n")
    print("  1. MERGE ONLY - Combine multiple GeoTIFFs into one")
    print("  2. REPROJECT ONLY - Change coordinate system of one file")
    print("  3. BOTH - Merge AND reproject (recommended)")
    print("  4. Cancel")
    
    while True:
        choice = input("\nChoose (1-4): ").strip()
        if choice in ['1', '2', '3', '4']:
            return int(choice)
        print("Please enter 1, 2, 3, or 4")

def get_crs_choice():
    """Get target CRS from user"""
    print("\n🎯 CHOOSE TARGET COORDINATE SYSTEM:\n")
    print("  1. WGS84 (EPSG:4326) - For web maps, Google Earth")
    print("  2. UTM Zone - Automatic based on image location")
    print("  3. Enter custom EPSG code (e.g., 3857, 32633)")
    print("  4. Keep original CRS")
    
    while True:
        choice = input("\nChoose (1-4): ").strip()
        if choice == '1':
            return "EPSG:4326"
        elif choice == '2':
            return "AUTO_UTM"
        elif choice == '3':
            code = input("Enter EPSG code (e.g., 3857): ").strip()
            return f"EPSG:{code}"
        elif choice == '4':
            return "KEEP"
        else:
            print("Invalid choice. Try again.")

def merge_only(files, output_name):
    """Just merge files without reprojection"""
    logger.log(f"Starting MERGE ONLY: {len(files)} files -> {output_name}")
    
    try:
        # Open all files
        src_files = []
        for i, f in enumerate(files, 1):
            logger.log(f"Opening file {i}/{len(files)}: {f}")
            src = rasterio.open(f)
            src_files.append(src)
        
        # Merge
        logger.log("Merging files...")
        mosaic, out_trans = merge(src_files)
        logger.log(f"Mosaic created: {mosaic.shape}")
        
        # Save
        meta = src_files[0].meta.copy()
        meta.update({
            'height': mosaic.shape[1],
            'width': mosaic.shape[2],
            'transform': out_trans,
            'compress': 'deflate'
        })
        
        logger.log(f"Saving to {output_name}...")
        with rasterio.open(output_name, 'w', **meta) as dst:
            dst.write(mosaic)
        
        # Close source files
        for src in src_files:
            src.close()
        
        return True
        
    except Exception as e:
        logger.log(f"Merge failed: {str(e)}", "ERROR")
        return False

def reproject_only(input_file, output_name, target_crs):
    """Just reproject a single file"""
    logger.log(f"Starting REPROJECT ONLY: {input_file} -> {target_crs}")
    
    try:
        with rasterio.open(input_file) as src:
            logger.log(f"Source: {src.width}×{src.height}, CRS: {src.crs}")
            
            if target_crs == "KEEP" or str(src.crs) == str(target_crs):
                logger.log("No reprojection needed - copying file")
                import shutil
                shutil.copy2(input_file, output_name)
                return True
            
            # Calculate transformation
            logger.log("Calculating transform...")
            transform, width, height = calculate_default_transform(
                src.crs, target_crs,
                src.width, src.height,
                *src.bounds
            )
            
            # Prepare output
            meta = src.meta.copy()
            meta.update({
                'crs': target_crs,
                'transform': transform,
                'width': width,
                'height': height,
                'compress': 'deflate'
            })
            
            # Reproject
            logger.log("Reprojecting bands...")
            with rasterio.open(output_name, 'w', **meta) as dst:
                for band in range(1, src.count + 1):
                    logger.log(f"  Band {band}/{src.count}", end='')
                    reproject(
                        source=rasterio.band(src, band),
                        destination=rasterio.band(dst, band),
                        src_transform=src.transform,
                        src_crs=src.crs,
                        dst_transform=transform,
                        dst_crs=target_crs,
                        resampling=Resampling.bilinear
                    )
            
            return True
            
    except Exception as e:
        logger.log(f"Reproject failed: {str(e)}", "ERROR")
        return False

def merge_and_reproject(files, output_name, target_crs):
    """Merge AND reproject"""
    logger.log(f"Starting MERGE & REPROJECT: {len(files)} files -> {target_crs}")
    
    try:
        # Open all files
        src_files = []
        for i, f in enumerate(files, 1):
            logger.log(f"Opening file {i}/{len(files)}: {f}")
            src = rasterio.open(f)
            src_files.append(src)
        
        # Merge
        logger.log("Merging files...")
        mosaic, out_trans = merge(src_files)
        logger.log(f"Mosaic created: {mosaic.shape}")
        
        # Determine target CRS
        if target_crs == "AUTO_UTM":
            with rasterio.open(files[0]) as sample:
                bounds = sample.bounds
                center_lon = (bounds.left + bounds.right) / 2
                utm_zone = int((center_lon + 180) // 6) + 1
                hemisphere = 'north' if bounds.bottom >= 0 else 'south'
                epsg_code = 32600 + utm_zone if hemisphere == 'north' else 32700 + utm_zone
                target_crs = f"EPSG:{epsg_code}"
                logger.log(f"Auto-selected: {target_crs}")
        elif target_crs == "KEEP":
            target_crs = src_files[0].crs
            logger.log(f"Keeping original: {target_crs}")
        
        # Reproject if needed
        if target_crs != "KEEP" and str(src_files[0].crs) != str(target_crs):
            logger.log(f"Reprojecting to {target_crs}...")
            
            with rasterio.open(files[0]) as ref_src:
                transform, width, height = calculate_default_transform(
                    ref_src.crs, target_crs,
                    mosaic.shape[2], mosaic.shape[1],
                    *ref_src.bounds
                )
                
                # Prepare output
                meta = ref_src.meta.copy()
                meta.update({
                    'crs': target_crs,
                    'transform': transform,
                    'width': width,
                    'height': height,
                    'count': mosaic.shape[0],
                    'compress': 'deflate',
                    'tiled': True
                })
                
                # Reproject
                logger.log("Reprojecting bands...")
                with rasterio.open(output_name, 'w', **meta) as dst:
                    for band in range(1, mosaic.shape[0] + 1):
                        logger.log(f"  Band {band}/{mosaic.shape[0]}")
                        reproject(
                            source=mosaic[band-1],
                            destination=rasterio.band(dst, band),
                            src_transform=ref_src.transform,
                            src_crs=ref_src.crs,
                            dst_transform=transform,
                            dst_crs=target_crs,
                            resampling=Resampling.bilinear
                        )
        else:
            logger.log("No reprojection needed - saving merged file")
            meta = src_files[0].meta.copy()
            meta.update({
                'height': mosaic.shape[1],
                'width': mosaic.shape[2],
                'transform': out_trans,
                'compress': 'deflate'
            })
            
            with rasterio.open(output_name, 'w', **meta) as dst:
                dst.write(mosaic)
        
        # Close source files
        for src in src_files:
            src.close()
        
        return True
        
    except Exception as e:
        logger.log(f"Processing failed: {str(e)}", "ERROR")
        return False

def show_results(output_name):
    """Show information about the output file"""
    if os.path.exists(output_name):
        size_mb = os.path.getsize(output_name) / 1024 / 1024
        
        try:
            with rasterio.open(output_name) as src:
                print("\n" + "=" * 60)
                print("✅ PROCESSING COMPLETE!")
                print("=" * 60)
                print(f"\n📊 OUTPUT FILE INFO:")
                print(f"   Name: {output_name}")
                print(f"   Size: {size_mb:.1f} MB")
                print(f"   Dimensions: {src.width} × {src.height} pixels")
                print(f"   Bands: {src.count}")
                print(f"   CRS: {src.crs}")
                print(f"   Location: {os.path.abspath(output_name)}")
                
                # Show data type
                dtype = src.dtypes[0]
                print(f"   Data type: {dtype}")
                
                # Quick stats
                try:
                    data = src.read(1, window=((0, min(100, src.height)), (0, min(100, src.width))))
                    print(f"   Sample min/max: {data.min():.1f} / {data.max():.1f}")
                except:
                    pass
                    
        except Exception as e:
            print(f"\n📁 File saved: {output_name}")
            print(f"📏 Size: {size_mb:.1f} MB")
            print(f"⚠️  Could not read GeoTIFF info: {e}")
    else:
        print("\n❌ Output file was not created!")

def main():
    """Main function"""
    print_header()
    
    # Find files
    tif_files = find_tif_files()
    
    if not tif_files:
        print("\n❌ No GeoTIFF files found in current folder!")
        print("Place your .tif files here and run again.")
        input("\nPress Enter to exit...")
        return
    
    # Select files
    selected_files = select_files_interactive(tif_files)
    if not selected_files:
        logger.log("Operation cancelled by user", "INFO")
        return
    
    # Get processing mode
    mode = get_processing_mode()
    if mode == 4:
        logger.log("Operation cancelled", "INFO")
        return
    
    # Get output name
    print_header()
    default_name = "merged_result.tif" if mode != 2 else "reprojected.tif"
    output_name = input(f"\n📝 Output filename [{default_name}]: ").strip()
    if not output_name:
        output_name = default_name
    
    # Check if file exists
    if os.path.exists(output_name):
        overwrite = input(f"File '{output_name}' exists. Overwrite? (y/n): ").lower()
        if overwrite != 'y':
            logger.log("Operation cancelled - file exists", "INFO")
            return
    
    # Get CRS for modes 2 and 3
    target_crs = None
    if mode in [2, 3]:
        target_crs = get_crs_choice()
    
    print_header()
    print("\n🚀 STARTING PROCESSING...")
    print("=" * 60)
    print("Live log will appear below:")
    print("-" * 60)
    
    start_time = time.time()
    
    # Process based on mode
    success = False
    if mode == 1:  # Merge only
        success = merge_only(selected_files, output_name)
    elif mode == 2:  # Reproject only
        if len(selected_files) != 1:
            logger.log("Reproject only works with ONE file. Using first file.", "WARN")
        success = reproject_only(selected_files[0], output_name, target_crs)
    elif mode == 3:  # Both
        success = merge_and_reproject(selected_files, output_name, target_crs)
    
    # Calculate elapsed time
    elapsed = time.time() - start_time
    minutes = int(elapsed // 60)
    seconds = int(elapsed % 60)
    
    # Stop logger and print final logs
    time.sleep(0.5)  # Let logger catch up
    logger.stop()
    
    # Get remaining logs
    final_logs = logger.get_logs()
    for log in final_logs:
        print(f"  {log}")
    
    # Show results
    if success:
        show_results(output_name)
        print(f"\n⏱️  Processing time: {minutes}m {seconds}s")
    else:
        print("\n" + "=" * 60)
        print("❌ PROCESSING FAILED!")
        print("=" * 60)
        print("\n⚠️  Check the logs above for errors.")
    
    print("\n" + "=" * 60)
    input("\nPress Enter to exit...")

# Run the tool
if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Operation cancelled by user")
        logger.stop()
        input("\nPress Enter to exit...")
    except Exception as e:
        print(f"\n❌ Unexpected error: {str(e)}")
        logger.stop()
        input("\nPress Enter to exit...")