import json
import urllib.request
import time
import os
import subprocess

# ===== 네이버 주식 API 요청 =====
item_code = "373220"
url = f"https://m.stock.naver.com/api/stock/{item_code}/integration"
raw_data = urllib.request.urlopen(url).read()
json_data = json.loads(raw_data)

# ===== 우리가 찾을 날짜 =====
target_dates = ["20251111", "20250604"]   # ← 여기 수정됨

# ===== 날짜별 결과 저장 =====
results = {}

for day in json_data.get("dealTrendInfos", []):
    bizdate = day.get("bizdate")
    if bizdate in target_dates:
        results[bizdate] = {
            "종가": day.get("closePrice"),
            "거래량": day.get("accumulatedTradingVolume"),
            "외국인소진율": day.get("foreignerHoldRatio")
        }

# ===== 파일로 저장 =====
now = time.strftime("%Y-%m-%d_%H-%M-%S")
filename = f"stock_record_{now}.txt"

with open(filename, "w", encoding="utf-8") as f:
    for td in target_dates:
        f.write(f"날짜: {td}\n")
        if td in results:
            f.write(f"종가: {results[td]['종가']}\n")
            f.write(f"거래량: {results[td]['거래량']}\n")
            f.write(f"외국인소진율: {results[td]['외국인소진율']}\n")
        else:
            f.write("데이터 없음\n")
        f.write("\n")

# ===== Git 자동 업로드 =====
subprocess.run(["git", "add", "."])
subprocess.run(["git", "commit", "-m", f"자동 업로드: {filename}"])
subprocess.run(["git", "push"])


print("========== GitHub 업로드 완료 ==========")
print(f"파일 생성됨: {filename}")
