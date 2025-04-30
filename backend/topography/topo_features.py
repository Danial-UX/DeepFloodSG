import rasterio
import numpy as np
from rasterio.windows import Window
import os
from pathlib import Path
from pyproj import Transformer
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

current_dir = Path(__file__).parent

# DEM configuration
DEM_PATH = os.path.join(current_dir, 'dem_AW3D30_UTM.tif')
DRAINAGE_PATH = current_dir.parent / 'drainage' / 'drainage_density.tif'

# Default values when data is unavailable
DEFAULT_ELEVATION = 15.0
DEFAULT_SLOPE = 5.0
DEFAULT_ASPECT = 180.0
DEFAULT_DRAINAGE = 0.2


def compute_slope_aspect(dem_array, cellsize):
    """Calculate slope and aspect from a 3x3 DEM window."""
    if dem_array.shape != (3, 3):
        return None, None

    try:
        Z = dem_array.astype(np.float32)
        if np.any(np.isnan(Z)):
            return None, None

        dzdx = ((Z[0,2] + 2*Z[1,2] + Z[2,2]) - (Z[0,0] + 2*Z[1,0] + Z[2,0])) / (8 * cellsize)
        dzdy = ((Z[2,0] + 2*Z[2,1] + Z[2,2]) - (Z[0,0] + 2*Z[0,1] + Z[0,2])) / (8 * cellsize)

        slope_rad = np.arctan(np.sqrt(dzdx**2 + dzdy**2))
        slope_deg = np.degrees(slope_rad)

        aspect_rad = np.arctan2(dzdy, -dzdx)
        aspect_deg = np.degrees(aspect_rad)
        return slope_deg, (aspect_deg + 360) % 360  # Ensure 0-360 range
    
    except Exception as e:
        logger.error(f"Slope/aspect calculation failed: {e}")
        return None, None

def get_topo_features(lat, lon):
    """Get topographic features with robust error handling."""
    # Initialize with defaults
    elevation = DEFAULT_ELEVATION
    slope = DEFAULT_SLOPE
    aspect = DEFAULT_ASPECT
    drainage = DEFAULT_DRAINAGE

    # Check if coordinates are valid geographic coordinates
    if not (-180 <= lon <= 180) or not (-90 <= lat <= 90):
        logger.error(f"Invalid coordinates: {lon},{lat}")
        return elevation, slope, aspect, drainage

    if not os.path.exists(DEM_PATH):
        return elevation, slope, aspect, drainage

    try:
        with rasterio.open(DEM_PATH) as dem_src:
            # Transform WGS84 to UTM Zone 48N
            transformer = Transformer.from_crs("EPSG:4326", dem_src.crs, always_xy=True)
            try:
                x, y = transformer.transform(lon, lat)
            except Exception as e:
                logger.error(f"Coordinate transform failed: {e}")
                return elevation, slope, aspect, drainage

            # Check bounds in UTM coordinates
            if not (dem_src.bounds.left <= x <= dem_src.bounds.right and
                    dem_src.bounds.bottom <= y <= dem_src.bounds.top):
                logger.warning(f"Transformed coordinates {x},{y} outside DEM bounds")
                return elevation, slope, aspect, drainage
    
            # Get valid row/col indices
            row, col = dem_src.index(x, y)  # Changed to use transformed coordinates
            row = max(0, min(row, dem_src.height - 1))
            col = max(0, min(col, dem_src.width - 1))

            # Read elevation
            elevation = float(dem_src.read(1)[row, col])
            if dem_src.nodata is not None and elevation == dem_src.nodata:
                elevation = DEFAULT_ELEVATION

            # Calculate slope/aspect with safe windowing
            row_start = max(0, row - 1)
            row_end = min(dem_src.height, row + 2)
            col_start = max(0, col - 1)
            col_end = min(dem_src.width, col + 2)
            
            window = Window(col_start, row_start, 
                          col_end - col_start, 
                          row_end - row_start)
            
            dem_array = dem_src.read(1, window=window)
            if dem_src.nodata is not None:
                dem_array = np.where(dem_array == dem_src.nodata, np.nan, dem_array)

            if dem_array.size >= 9:  # At least 3x3
                # Pad array if at edges
                if dem_array.shape != (3, 3):
                    padded = np.full((3, 3), np.nan)
                    h, w = dem_array.shape
                    padded[:h, :w] = dem_array
                    dem_array = padded
                
                cellsize = dem_src.res[0]
                slope, aspect = compute_slope_aspect(dem_array, cellsize)

    except Exception as e:
        logger.error(f"DEM processing failed: {e}")

    # Process drainage density if exists (now properly outside DEM block)
    if os.path.exists(DRAINAGE_PATH):
        try:
            with rasterio.open(DRAINAGE_PATH) as drainage_src:
                if (drainage_src.bounds.left <= lon <= drainage_src.bounds.right and
                    drainage_src.bounds.bottom <= lat <= drainage_src.bounds.top):
                    
                    row, col = drainage_src.index(lon, lat)
                    row = max(0, min(row, drainage_src.height - 1))
                    col = max(0, min(col, drainage_src.width - 1))
                    
                    value = drainage_src.read(1)[row, col]
                    if drainage_src.nodata is None or value != drainage_src.nodata:
                        drainage = float(value)
        except Exception as e:
            logger.error(f"Drainage processing failed: {e}")

    return (
        elevation if elevation is not None else DEFAULT_ELEVATION,
        slope if slope is not None else DEFAULT_SLOPE,
        aspect if aspect is not None else DEFAULT_ASPECT,
        drainage if drainage is not None else DEFAULT_DRAINAGE
    )