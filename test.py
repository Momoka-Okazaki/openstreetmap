import geopandas as gpd

gdf = gpd.read_file("data/dakar_landuse_mix_latlon.geojson")

# 異常値を含むgeometryを抽出
def has_invalid_coords(geom):
    try:
        for x, y in geom.exterior.coords:
            if not (-90 <= y <= 90) or not (-180 <= x <= 180):
                return True
    except:
        return False
    return False

invalid_geoms = gdf[gdf.geometry.apply(has_invalid_coords)]

print(f"異常なgeometryの数: {len(invalid_geoms)}")
print(invalid_geoms.head())
