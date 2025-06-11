import osmnx as ox
import geopandas as gpd
from shapely.geometry import box
import pandas as pd

# 調査したい場所
place_name = "Dakar, Senegal"

# 1. 公共交通施設データをOSMから取得
public_transport_platforms = ox.features_from_place(place_name, tags={'public_transport': 'platform'})
bus_stops = ox.features_from_place(place_name, tags={'highway': 'bus_stop'})

# 2. 2つのデータを結合
pt = pd.concat([public_transport_platforms, bus_stops], ignore_index=True)

# 3. GeoDataFrameに変換
pt = gpd.GeoDataFrame(pt, geometry='geometry')

# 4. Dakarの境界ポリゴンを取得
area = ox.geocode_to_gdf(place_name)

# 5. グリッドサイズ（メートル）指定（500m四方）
grid_size = 0.005  # 約0.005度＝約500m（緯度方向のおおよその値）

# 6. Dakarの境界の範囲を取得
minx, miny, maxx, maxy = area.total_bounds

# 7. グリッドセルを作成
grid_cells = []
x = minx
while x < maxx:
    y = miny
    while y < maxy:
        grid_cells.append(box(x, y, x + grid_size, y + grid_size))
        y += grid_size
    x += grid_size

# 8. グリッドGeoDataFrame作成
grid = gpd.GeoDataFrame({'geometry': grid_cells})
grid.set_crs(epsg=4326, inplace=True)

# 9. 公共交通ポイントを空間結合でグリッドに紐付け（ポイントがどのセルに入るか）
joined = gpd.sjoin(pt, grid, how='left', predicate='within')

# 10. グリッドごとに公共交通施設の数をカウント
count_series = joined.groupby('index_right').size()

# 11. カウント結果をグリッドに追加
grid['pt_count'] = count_series
grid['pt_count'] = grid['pt_count'].fillna(0).astype(int)

# 12. 結果をGeoJSONファイルに保存
grid.to_file("dakar_public_transport_grid.geojson", driver='GeoJSON')

print("グリッド毎の公共交通施設数を計算し、dakar_public_transport_grid.geojsonに保存しました。")
