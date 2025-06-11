import osmnx as ox
import geopandas as gpd
import os

def main():
    output_dir = "data"
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, "dakar_landuse.geojson")

    place = "Dakar, Senegal"
    tags = {"landuse": True}

    # ここを変更
    landuse_gdf = ox.features_from_place(place, tags)

    print("Columns in landuse data:")
    print(landuse_gdf.columns)

    print("Sample data:")
    print(landuse_gdf.head())

    landuse_gdf.to_file(output_path, driver="GeoJSON")
    print(f"Saved landuse data to {output_path}")

if __name__ == "__main__":
    main()
