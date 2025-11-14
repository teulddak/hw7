import os
import requests
import csv
from datetime import datetime, timedelta
import math
import time
import urllib.parse

# ======================================================
# ⚙️ 서비스키 설정
# ======================================================

# 주인님이 준 "디코딩된 서비스키"
DECODED_KEY = "580565d89ab9b438d47e868d48ed7991af3cfb92447a00d7b33dc73e77e34246"

# 👉 기상청 API는 Python 환경에서 반드시 인코딩된 키를 요구
SERVICE_KEY = urllib.parse.quote(DECODED_KEY, safe="")

# ======================================================
# API 설정
# ======================================================
API_URL = "https://apis.data.go.kr/1360000/AsosHourlyInfoService/getWthrDataList"
STATION_ID = "108"  # 서울
OUTPUT_DIR = "./HW7_output"
os.makedirs(OUTPUT_DIR, exist_ok=True)


# ======================================================
# 📌 ASOS 시간구간 데이터 요청 함수
# ======================================================
def fetch_window(tag, start_dt, end_dt):
    print("\n=====================================================")
    print(f"📡 [{tag}] 데이터 요청 시작")
    print(f"▶ 기간: {start_dt} ~ {end_dt}")
    print("=====================================================")

    page_no = 1
    num_rows = 500
    all_rows = []

    while True:
        params = {
            "serviceKey": SERVICE_KEY,
            "dataType": "JSON",
            "dataCd": "ASOS",
            "dateCd": "HR",
            "startDt": start_dt.strftime("%Y%m%d"),
            "startHh": start_dt.strftime("%H"),
            "endDt": end_dt.strftime("%Y%m%d"),
            "endHh": end_dt.strftime("%H"),
            "stnIds": STATION_ID,
            "pageNo": page_no,
            "numOfRows": num_rows
        }

        response = requests.get(API_URL, params=params)
        response.raise_for_status()
        res_json = response.json()

        body = res_json.get("response", {}).get("body", {})
        items = body.get("items", {}).get("item", [])
        total_count = body.get("totalCount", 0)

        if not items:
            break

        print(f"📄 페이지 {page_no} 수집 ({len(items)}건)")
        all_rows.extend(items)

        max_pages = math.ceil(total_count / num_rows) if total_count else 1
        if page_no >= max_pages:
            break

        page_no += 1
        time.sleep(0.1)

    csv_path = os.path.join(OUTPUT_DIR, f"{tag}_stn{STATION_ID}.csv")

    if all_rows:
        keys = sorted({k for row in all_rows for k in row.keys()})

        with open(csv_path, "w", newline="", encoding="utf-8-sig") as f:
            writer = csv.DictWriter(f, fieldnames=keys)
            writer.writeheader()
            writer.writerows(all_rows)

        print("-----------------------------------------------------")
        print(f"✅ [{tag}] 저장 완료!")
        print(f"📊 총 {len(all_rows)}건")
        print(f"💾 CSV 위치: {csv_path}")
        print("-----------------------------------------------------")
    else:
        print(f"❌ [{tag}] 데이터 없음")

    return all_rows


# ======================================================
# 📌 과제 요구 시간 구간
# ======================================================

# 1) 2024-12-04 15시~18시
win1_start = datetime(2024, 12, 4, 15)
win1_end   = datetime(2024, 12, 4, 18)

# 2) 2025-06-04 12시~16시
win2_start = datetime(2025, 6, 4, 12)
win2_end   = datetime(2025, 6, 4, 16)

# 3) 실행일 기준 2일 전 00~03시
now = datetime.now()
before2 = now - timedelta(days=2)
win3_start = before2.replace(hour=0, minute=0, second=0, microsecond=0)
win3_end   = win3_start.replace(hour=3)

windows = [
    ("window1_20241204_15_18", win1_start, win1_end),
    ("window2_20250604_12_16", win2_start, win2_end),
    ("window3_execminus2_00_03", win3_start, win3_end)
]


# ======================================================
# 🚀 실행부
# ======================================================
print("\n=============================================")
print("  HW7 기상청 ASOS 시간자료 수집 프로그램 실행")
print("=============================================")

total = 0
for tag, s, e in windows:
    total += len(fetch_window(tag, s, e))

print("\n=============================================")
print(f"🎉 전체 데이터 총합: {total}건")
print(f"📁 모든 결과는 HW7_output 폴더에 저장되었습니다.")
print("=============================================")
