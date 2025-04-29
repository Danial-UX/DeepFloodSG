import rasterio
import numpy as np
import pandas as pd
from rasterio.warp import Resampling

# Resample raster function to align rasters for slope, aspect, and drainage density
def resample_raster(input_path, match_path, output_path):
    with rasterio.open(match_path) as match:
        dst_transform = match.transform
        dst_crs = match.crs
        dst_width = match.width
        dst_height = match.height

    with rasterio.open(input_path) as src:
        data = src.read(
            out_shape=(src.count, dst_height, dst_width),
            resampling=Resampling.bilinear
        )

        kwargs = src.meta.copy()
        kwargs.update({
            'crs': dst_crs,
            'transform': dst_transform,
            'width': dst_width,
            'height': dst_height
        })

        with rasterio.open(output_path, 'w', **kwargs) as dst:
            dst.write(data)

# Open all rasters
slope_src = rasterio.open('../topography/slope.tif')
aspect_src = rasterio.open('../topography/aspect.tif')
drainage_src = rasterio.open('../drainage/drainage_density.tif')

# Check alignment
if slope_src.shape != aspect_src.shape or slope_src.shape != drainage_src.shape:
    print("Shapes differ! Resampling...")
    resample_raster('../topography/aspect.tif', '../topography/slope.tif', 'aspect_resampled.tif')
    resample_raster('../drainage/drainage_density.tif', '../topography/slope.tif', 'drainage_density_resampled.tif')
    aspect_src = rasterio.open('aspect_resampled.tif')
    drainage_src = rasterio.open('drainage_density_resampled.tif')
else:
    print("Shapes already aligned!")

# Stack raster
meta = slope_src.meta.copy()
meta.update(count=3)  # 3 layers

with rasterio.open('stacked_features.tif', 'w', **meta) as dst:
    dst.write(slope_src.read(1), 1)      # Band 1: Slope
    dst.write(aspect_src.read(1), 2)     # Band 2: Aspect
    dst.write(drainage_src.read(1), 3)   # Band 3: Drainage

print("Raster stack created!")

# Extract raster values at CSV points
df = pd.read_csv('../flood_prediction/data_with_slope_aspect.csv')

# Important: RasterIO expects (x, y) = (longitude, latitude)
coords = list(zip(df['longitude'], df['latitude']))

# Sample raster
stacked = rasterio.open('stacked_features.tif')
samples = list(stacked.sample(coords))

# Add raster features to dataframe
df['slope_percent'] = [s[0] for s in samples]
df['aspect_degrees'] = [s[1] for s in samples]
df['drainage_density'] = [s[2] for s in samples]

print("Raster features extracted and added to dataframe!")

# Save ready-to-train dataset
df.to_csv('../flood_prediction/flood_training_data.csv', index=False)
print("Data saved as flood_training_data.csv!")
