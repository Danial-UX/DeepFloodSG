import rasterio
import numpy as np
from rasterio.windows import Window
import os
from pathlib import Path

current_dir = Path(__file__).parent

DEM_PATH = os.path.join(current_dir, 'dem_AW3D30_UTM.tif')
DRAINAGE_PATH = current_dir.parent / 'drainage' / 'drainage_density.tif'

def compute_slope_aspect(dem_array, cellsize):
    """
    Calculates slope and aspect using Horn's method from a 3x3 DEM window.
    Assumes DEM is projected in meters (e.g., UTM) and square pixels.
    """
    if dem_array.shape != (3, 3):
        return None, None

    Z = dem_array.astype(np.float32)

    if np.any(np.isnan(Z)):
        return None, None

    dzdx = ((Z[0,2] + 2*Z[1,2] + Z[2,2]) - (Z[0,0] + 2*Z[1,0] + Z[2,0])) / (8 * cellsize)
    dzdy = ((Z[2,0] + 2*Z[2,1] + Z[2,2]) - (Z[0,0] + 2*Z[0,1] + Z[0,2])) / (8 * cellsize)

    slope_rad = np.arctan(np.sqrt(dzdx**2 + dzdy**2))
    slope_deg = np.degrees(slope_rad)

    aspect_rad = np.arctan2(dzdy, -dzdx)
    aspect_deg = np.degrees(aspect_rad)
    if aspect_deg < 0:
        aspect_deg += 360

    return slope_deg, aspect_deg

def get_topo_features(lat, lon):
    elevation = None
    slope = None
    aspect = None
    drainage_density = None

    with rasterio.open(DEM_PATH) as dem_src:
        try:
            # Get row, col from lat/lon
            row, col = dem_src.index(lon, lat)
            elevation = dem_src.read(1)[row, col]

            # 3x3 window for slope/aspect
            window = Window(col - 1, row - 1, 3, 3)
            dem_array = dem_src.read(1, window=window)

            # Replace nodata with NaN
            nodata = dem_src.nodata
            if nodata is not None:
                dem_array = np.where(dem_array == nodata, np.nan, dem_array)

            if dem_array.shape == (3, 3):
                cellsize = dem_src.res[0]  # Assuming square pixels
                slope, aspect = compute_slope_aspect(dem_array, cellsize)
        except Exception as e:
            print(f"DEM processing error: {e}")

    with rasterio.open(DRAINAGE_PATH) as drainage_src:
        try:
            row, col = drainage_src.index(lon, lat)
            value = drainage_src.read(1)[row, col]
            if drainage_src.nodata is None or value != drainage_src.nodata:
                drainage_density = float(value)
        except Exception as e:
            print(f"Drainage processing error: {e}")

    return elevation, slope, aspect, drainage_density