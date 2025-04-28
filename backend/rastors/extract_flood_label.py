import rasterio
from rasterio.features import rasterize
import geopandas as gpd
import pandas as pd
from shapely.geometry import Point
import numpy as np

df = pd.read_csv('../flood-prediction/data_with_slope_aspect.csv')

# Create GeoDataFrame
gdf = gpd.GeoDataFrame(df, geometry=gpd.points_from_xy(df.longitude, df.latitude))
gdf.set_crs(epsg=4326, inplace=True)  # WGS84 lat/lon

# Open reference raster (stacked_features.tif)
ref_raster = rasterio.open('stacked_features.tif')

# Reproject points to match raster CRS
gdf = gdf.to_crs(ref_raster.crs)

# Create list of (geometry, value) pairs
shapes = ((geom, value) for geom, value in zip(gdf.geometry, gdf.flood_occurred))

# Rasterize: default background=255 (means unknown), flood=1, no flood=0
label_raster = rasterize(
    shapes=shapes,
    out_shape=(ref_raster.height, ref_raster.width),
    transform=ref_raster.transform,
    fill=255,  # background: unknown
    dtype=rasterio.uint8
)

# Save flood_label.tif
out_meta = ref_raster.meta.copy()
out_meta.update({
    "count": 1,
    "dtype": 'uint8',
    "nodata": 255
})

# Use 1 for flood points
# Use 0 for non-flood points (assuming your data has these values)
# Use 255 for unknown/background areas

with rasterio.open('../flood-prediction/flood_label.tif', 'w', **out_meta) as dst:
    dst.write(label_raster, 1)

print("flood_label.tif created successfully!")