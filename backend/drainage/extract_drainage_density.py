import geopandas as gpd
import numpy as np
import rasterio
from rasterio.features import rasterize
from shapely.geometry import box
import shapely

# Drainage and canals data extracted from OpenStreetMap
drainage = gpd.read_file('drainage_and_canals.geojson')

# Remove rows with empty or invalid geometries
drainage = drainage[~drainage.geometry.is_empty & drainage.geometry.is_valid]

# Check if any valid geometries remain
if len(drainage) == 0:
    raise ValueError("No valid geometries found in the GeoDataFrame!")

# Define raster parameters
bounds = drainage.total_bounds  # (minx, miny, maxx, maxy)
resolution = 10  # meters per pixel

width = max(1, int((bounds[2] - bounds[0]) / resolution))
height = max(1, int((bounds[3] - bounds[1]) / resolution))

transform = rasterio.transform.from_origin(bounds[0], bounds[3], resolution, resolution)

# Create an empty array to store total drain length per pixel
density_array = np.zeros((height, width), dtype=np.float32)

# Function to split geometries into small pieces
def split_line_to_pixels(line, resolution):
    """Splits a LineString into small segments ~resolution size."""
    if line.length <= resolution:
        return [line]
    num_segments = int(line.length // resolution) + 1
    points = [line.interpolate(float(i)/num_segments, normalized=True) for i in range(num_segments+1)]
    return [shapely.geometry.LineString([points[i], points[i+1]]) for i in range(len(points)-1)]

# Split lines into small segments to better distribute density
all_segments = []
for geom in drainage.geometry:
    if geom is not None and geom.is_valid:
        if geom.type == 'LineString':
            all_segments.extend(split_line_to_pixels(geom, resolution))
        elif geom.type == 'MultiLineString':
            for line in geom:
                all_segments.extend(split_line_to_pixels(line, resolution))

# Rasterize: for each segment, add its length to the corresponding pixel
shapes = [(seg, seg.length) for seg in all_segments]

# Rasterize
raster = rasterize(
    shapes,
    out_shape=(height, width),
    transform=transform,
    fill=0,
    all_touched=True,
    dtype='float32'
)

# Save the drainage density raster
with rasterio.open(
    'drainage_density.tif', 'w',
    driver='GTiff',
    height=height,
    width=width,
    count=1,
    dtype='float32',
    crs=drainage.crs,
    transform=transform
) as dst:
    dst.write(raster, 1)

print("Drainage density raster saved!")
