import geopandas as gpd
import pandas as pd
from shapely.geometry import box

def calc_landuse_mix(geometry, landuse_gdf):
    # 1セルあたりのポリゴンにクリップ（切り出し）
    clipped = gpd.clip(landuse_gdf, geometry)
    if clipped.empty:
        return 0.0
    
    # 土地利用別の面積割合を計算
    clipped['area'] = clipped.geometry.area
    total_area = clipped['area'].sum()
    if total_area == 0:
        return 0.0

    proportions = clipped.groupby('landuse')['area'].sum() / total_area
    
    # 混合度指標（シャノン多様度指数など）
    import numpy as np
    landuse_mix = -sum(p * np.log(p) for p in proportions if p > 0)
    return landuse_mix

def main():
    # 土地利用データ読み込み
    landuse_gdf = gpd.read_file('data/dakar_landuse.geojson')
    landuse_gdf = landuse_gdf.to_crs(epsg=3857)  # メートル単位の投影法に変換
    
    # 解析範囲（例としてダカール中心部付近のグリッド生成）
    minx, miny, maxx, maxy = landuse_gdf.total_bounds
    grid_size = 500  # 500m四方のグリッド
    
    # グリッド作成
    grids = []
    x = minx
    while x < maxx:
        y = miny
        while y < maxy:
            grids.append(box(x, y, x + grid_size, y + grid_size))
            y += grid_size
        x += grid_size
    grid_gdf = gpd.GeoDataFrame(geometry=grids, crs=landuse_gdf.crs)
    
    # 各グリッドに土地利用混合度を計算
    grid_gdf['landuse_mix'] = grid_gdf.geometry.apply(lambda geom: calc_landuse_mix(geom, landuse_gdf))
    
    # 結果保存
    grid_gdf.to_file('data/dakar_landuse_mix.geojson', driver='GeoJSON')
    print("土地利用混合度の計算が完了し、data/dakar_landuse_mix.geojsonに保存しました。")

if __name__ == "__main__":
    main()
