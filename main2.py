import json
import urllib.request

import json
import urllib.request

item_code = "373220"  # LG에너지솔루션
url = f"https://m.stock.naver.com/api/stock/{item_code}/integration"

# API 요청
raw_data = urllib.request.urlopen(url).read()
json_data = json.loads(raw_data)

# 우리가 찾을 날짜
target_dates = ["20251111", "20241204"]

# 출력 데이터 저장
results = {}

for day in json_data["dealTrendInfos"]:
    bizdate = day["bizdate"]

    if bizdate in target_dates:
        results[bizdate] = {
            "종가": day.get("closePrice", None),
            "거래량": day.get("accumulatedTradingVolume", None),
            "외국인소진율": day.get("foreignerHoldRatio", None)
        }

# 결과 출력
for d, info in results.items():
    print(f"==== {d} ====")
    for k, v in info.items():
        print(f"{k}: {v}")
    print()
