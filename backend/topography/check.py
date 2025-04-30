import rasterio

file_path = "/Users/rachel/Downloads/DeepFloodSG-1/backend/topography/dem_AW3D30.tif"
with rasterio.open(file_path) as src:
    print("DEM resolution:", src.res)  # (x_res, y_res)