import pandas as pd
from haversine import haversine

# 被験者の居住地（例）
home_lat = 14.75
home_lon = -17.48
home = (home_lat, home_lon)


# CSVファイルの読み込み
df = df = pd.read_csv('/Users/okazakimomoka/google-maps-scraper/data/dakar_public_transport.csv')


# 1km以内か判定する関数
def is_within_1km(row):
    point = (row['lat'], row['lon'])
    return haversine(home, point) <= 1

# 条件に合う行だけ抽出
df_within_1km = df[df.apply(is_within_1km, axis=1)]

# 件数を表示
print(f"被験者の居住地から1km圏内の公共交通機関数: {len(df_within_1km)}")

# 抽出したデータをCSVに保存
df_within_1km.to_csv('public_transport_within_1km.csv', index=False)
print("1km圏内の公共交通機関データをCSVに保存しました。")