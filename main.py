import json
import urllib.request
import yfinance as yf
import time
import subprocess

# ===============================
# 설정 부분
# ===============================
item_code = "373220"              # LG에너지솔루션
ticker = "373220.KS"              # 야후 파이낸스 코드
loop_count = 7                    # 1분마다 7번 실행
interval = 60                     # 1분 = 60초

# 과거 원하는 날짜
target_dates = ["20250604", "20251111"]   # 문자열 그대로 사용

# 야후 파이낸스용 날짜 변환
date_map = {
    "20250604": ("2025-06-03", "2025-06-05"),
    "20251111": ("2025-11-10", "2025-11-12"),
}

# ===============================
# 7회 반복 실행 시작
# ===============================
for i in range(loop_count):
    print(f"\n===== 실행 {i+1}/{loop_count} =====")

    # ============================
    # 1) 네이버 API → 오늘 데이터
    # ============================
    try:
        nav_url = f"https://m.stock.naver.com/api/stock/{item_code}/integration"
        raw_nav = urllib.request.urlopen(nav_url).read()
        nav_json = json.loads(raw_nav)
        today_info = nav_json["totalInfos"]

        today_data = {
            "시가": None,
            "고가": None,
            "저가": None,
            "거래량": None,
            "외국인소진율": None,
        }

        for info in today_info:
            if info["key"] == "시가":
                today_data["시가"] = info["value"]
            if info["key"] == "고가":
                today_data["고가"] = info["value"]
            if info["key"] == "저가":
                today_data["저가"] = info["value"]
            if info["key"] == "거래량":
                today_data["거래량"] = info["value"]
            if info["key"] == "외인소진율" or info["key"] == "외국인소진율":
                today_data["외국인소진율"] = info["value"]

    except:
        print("⚠️ 네이버(오늘 데이터) 불러오기 실패")
        today_data = None

    # ============================
    # 2) 야후 → 과거 데이터
    # ============================
    past_result = {}

    try:
        for td in target_dates:
            start, end = date_map[td]
            df = yf.download(ticker, start=start, end=end)

            if len(df) > 0:
                row = df.iloc[0]
                past_result[td] = {
                    "시가": f"{row['Open']:.2f}",
                    "고가": f"{row['High']:.2f}",
                    "저가": f"{row['Low']:.2f}",
                    "종가": f"{row['Close']:.2f}",
                    "거래량": str(int(row['Volume'])),
                }
            else:
                past_result[td] = None
    except:
        print("⚠️ 야후(과거 데이터) 불러오기 실패")

    # ============================
    # 3) 파일 저장
    # ============================
    filename = f"stock_record_run{i+1}.txt"

    with open(filename, "w", encoding="utf-8") as f:
        f.write("======= 네이버 오늘 데이터 =======\n")
        if today_data:
            for k, v in today_data.items():
                f.write(f"{k}: {v}\n")
        else:
            f.write("오늘 데이터 없음\n")

        f.write("\n======= 과거 데이터(야후) =======\n")
        for td in target_dates:
            f.write(f"\n날짜: {td}\n")
            if past_result.get(td):
                for k, v in past_result[td].items():
                    f.write(f"{k}: {v}\n")
            else:
                f.write("데이터 없음\n")

    # ============================
    # 4) Git 자동 업로드
    # ============================
    subprocess.run(["git", "add", "."])
    subprocess.run(["git", "commit", "-m", f"자동 업로드: {filename}"])
    subprocess.run(["git", "push"])

    print(f"📌 업로드 완료 → {filename}")

    # 다음 실행을 위해 1분 대기 (마지막 반복은 제외)
    if i < loop_count - 1:
        time.sleep(interval)

print("\n===== 전체 작업 완료 =====")
