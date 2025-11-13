import json
import urllib.request
import time
import subprocess

# ===== 종목 코드 =====
item_code = "373220"

# ===== 찾을 날짜 =====
target_dates = ["20251111", "20250604"]

# ===== 헤더 설정 (네이버 차트 API는 필수) =====
headers = {
    "User-Agent": "Mozilla/5.0"
}

# ===== 1분마다 7번 반복 =====
for i in range(7):

    print(f"\n===== 실행 {i+1}/7 =====")

    # ===== 1) 차트 API (시가/고가/저가/종가/거래량) =====
    chart_url = f"https://api.stock.naver.com/chart/domestic/item/{item_code}?periodType=day&count=600"
    req = urllib.request.Request(chart_url, headers=headers)
    chart_raw = urllib.request.urlopen(req).read()
    chart_json = json.loads(chart_raw)

    # JSON 구조 확인 후 파싱
    chart_data = {}
    if "result" in chart_json:
        for day in chart_json["result"]["chartDatas"]:
            bizdate = day.get("localDate")
            chart_data[bizdate] = {
                "시가": day.get("openPrice"),
                "고가": day.get("highPrice"),
                "저가": day.get("lowPrice"),
                "종가": day.get("closePrice"),
                "거래량": day.get("volume")
            }
    else:
        print("⚠️ chart API에서 데이터를 받지 못했습니다.")

    # ===== 2) 외국인 소진율 =====
    integ_url = f"https://m.stock.naver.com/api/stock/{item_code}/integration"
    integ_raw = urllib.request.urlopen(integ_url).read()
    integ_json = json.loads(integ_raw)

    foreign_data = {}
    for day in integ_json.get("dealTrendInfos", []):
        foreign_data[day["bizdate"]] = day.get("foreignerHoldRatio")

    # ===== 3) 파일 저장 =====
    now = time.strftime("%Y-%m-%d_%H-%M-%S")
    filename = f"stock_record_{now}.txt"

    with open(filename, "w", encoding="utf-8") as f:
        for td in target_dates:
            f.write(f"날짜: {td}\n")

            if td in chart_data:
                f.write(f"시가: {chart_data[td]['시가']}\n")
                f.write(f"고가: {chart_data[td]['고가']}\n")
                f.write(f"저가: {chart_data[td]['저가']}\n")
                f.write(f"종가: {chart_data[td]['종가']}\n")
                f.write(f"거래량: {chart_data[td]['거래량']}\n")
            else:
                f.write("시가/고가/저가/종가/거래량: 데이터 없음\n")

            if td in foreign_data:
                f.write(f"외국인소진율: {foreign_data[td]}\n")
            else:
                f.write("외국인소진율: 데이터 없음\n")

            f.write("\n")

    # ===== 4) GitHub 자동 업로드 =====
    subprocess.run(["git", "add", "."])
    subprocess.run(["git", "commit", "-m", f"자동 업로드: {filename}"])
    subprocess.run(["git", "push"])

    print(f"파일 업로드 완료 → {filename}")

    if i < 6:
        time.sleep(60)

print("\n===== 전체 7회 업로드 완료 =====")
