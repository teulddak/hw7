import json
import urllib.request
import time
import subprocess

item_code = "373220"
target_dates = ["20251111", "20250604"]

# ===== 네이버 차트 API 강제 헤더 =====
headers = {
    "User-Agent": "Mozilla/5.0",
    "Referer": f"https://m.stock.naver.com/domestic/stock/{item_code}",
    "Accept": "application/json"
}

for i in range(7):

    print(f"\n===== 실행 {i+1}/7 =====")

    # ===== 1) 차트 API 요청 =====
    chart_url = f"https://api.stock.naver.com/chart/domestic/item/{item_code}?periodType=day&count=600"
    req = urllib.request.Request(chart_url, headers=headers)
    chart_raw = urllib.request.urlopen(req).read()
    chart_json = json.loads(chart_raw)

    chart_data = {}

    # JSON 구조가 맞는지 확인
    if "result" in chart_json and "chartDatas" in chart_json["result"]:
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
        print("⚠️ 차트 API 응답 실패. 헤더 문제 혹은 API 차단.")

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

    # ===== 4) Git 자동 업로드 =====
    subprocess.run(["git", "add", "."])
    subprocess.run(["git", "commit", "-m", f"자동 업로드: {filename}"])
    subprocess.run(["git", "push"])

    print(f"파일 업로드 완료 → {filename}")

    if i < 6:
        time.sleep(60)

print("\n===== 전체 7회 업로드 완료 =====")
