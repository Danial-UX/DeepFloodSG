import pandas as pd
import rasterio
from rasterio.sample import sample_gen

df = pd.read_csv('../flood-prediction/flood_data.csv')

slope_raster = rasterio.open('slope.tif')
aspect_raster = rasterio.open('aspect.tif')

coords = list(zip(df['longitude'], df['latitude']))

slope_values = [val[0] for val in slope_raster.sample(coords)]
aspect_values = [val[0] for val in aspect_raster.sample(coords)]

df['slope_percent'] = slope_values
df['aspect_degrees'] = aspect_values

df.to_csv('data_with_slope_aspect.csv', index=False)