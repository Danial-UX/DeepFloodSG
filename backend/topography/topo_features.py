import rasterio
import richdem as rd
import numpy as np
from rasterio.windows import Window

DEM_PATH = 'backend/topography/dem_AW3D30.tif'
DRAINAGE_PATH = 'backend/drainage/drainage_density.tif'

def get_topo_features(lat, lon):
    elevation = None
    slope = None
    aspect = None
    drainage_density = None

    # Elevation, Slope, Aspect
    with rasterio.open(DEM_PATH) as dem_src:
        try:
            row, col = dem_src.index(lon, lat)
            elevation = dem_src.read(1)[row, col]

            # Read a 3x3 window to calculate slope/aspect
            window = Window(col - 1, row - 1, 3, 3)
            dem_array = dem_src.read(1, window=window)

            if dem_array.shape == (3, 3) and np.all(dem_array != dem_src.nodata):
                dem = rd.rdarray(dem_array.astype('float32'), no_data=dem_src.nodata)
                dem.geotransform = [0, 1, 0, 0, 0, -1] 
                slope = float(rd.TerrainAttribute(dem, attrib='slope_degrees')[1, 1])
                aspect = float(rd.TerrainAttribute(dem, attrib='aspect')[1, 1])
        except:
            pass

    # Drainage Density
    with rasterio.open(DRAINAGE_PATH) as drainage_src:
        try:
            row, col = drainage_src.index(lon, lat)
            value = drainage_src.read(1)[row, col]
            if value != drainage_src.nodata:
                drainage_density = float(value)
        except:
            pass

    return elevation, slope, aspect, drainage_density
