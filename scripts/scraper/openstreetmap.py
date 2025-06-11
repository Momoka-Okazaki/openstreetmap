import requests
import pandas as pd

# Overpass APIにクエリを投げて公共交通機関データを取得する例
overpass_url = "http://overpass-api.de/api/interpreter"
query = """
[out:json];
area[name="Dakar"];
(
  node["public_transport"](area);
  way["public_transport"](area);
  relation["public_transport"](area);
);
out center;
"""
response = requests.get(overpass_url, params={'data': query})
data = response.json()

# ここでdataの中から必要な情報を抽出してリストにまとめる
elements = data['elements']
records = []
for elem in elements:
    if 'lat' in elem and 'lon' in elem:
        lat = elem['lat']
        lon = elem['lon']
    elif 'center' in elem:
        lat = elem['center']['lat']
        lon = elem['center']['lon']
    else:
        lat = None
        lon = None
    name = elem['tags'].get('name') if 'tags' in elem else None
    records.append({'id': elem['id'], 'name': name, 'lat': lat, 'lon': lon})

# DataFrameに変換
df = pd.DataFrame(records)

print(df.head())

# CSV保存
df.to_csv('/Users/okazakimomoka/google-maps-scraper/data/dakar_public_transport.csv', index=False)

df.to_csv('/Users/okazakimomoka/google-maps-scraper/data/dakar_public_transport.csv', index=False)
print("CSVファイルを保存しました。")

