import json
import urllib.request
import time
import datetime
import os
import subprocess


# ------------------------------------------
# 1) 네이버 API에서 현재 가격 정보 가져오기
# ------------------------------------------
def fetch_stock_data(item_code="373220"):
    url = f"https://m.stock.naver.com/api/stock/{item_code}/integration"
    raw_data = urllib.request.urlopen(url).read()
    data = json.loads(raw_data)

    # 최신 날짜 데이터(하루 단위) 추출
    today_info = data["dealTrendInfos"][0]

    result = {
        "날짜": today_info["bizdate"],
        "종가": today_info.get("closePrice"),
        "고가": today_info.get("compareToPreviousClosePrice"),
        "거래량": today_info.get("accumulatedTradingVolume"),
        "외국인소진율": today_info.get("foreignerHoldRatio")
    }

    return result


# ------------------------------------------
# 2) 데이터를 파일에 저장하기
# ------------------------------------------
def save_to_file(data):
    today = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    filename = f"stock_record_{today}.txt"

    with open(filename, "w", encoding="utf-8") as f:
        for k, v in data.items():
            f.write(f"{k}: {v}\n")

    print(f"[저장 완료] {filename}")
    return filename


# ------------------------------------------
# 3) GitHub 자동 업로드
# ------------------------------------------
def git_push(filename):
    try:
        subprocess.run(["git", "add", filename], check=True)
        subprocess.run(["git", "commit", "-m", f"자동 업로드: {filename}"], check=True)
        subprocess.run(["git", "push", "origin", "main"], check=True)
        print("[Git 업로드 완료]")
    except Exception as e:
        print("Git 업로드 실패:", e)


# ------------------------------------------
# 4) 1분마다 7번 반복 실행
# ------------------------------------------
def main_loop():
    for i in range(7):
        print(f"\n===== {i + 1} / 7 번째 실행 =====")

        # API 호출
        data = fetch_stock_data()

        # 파일 저장
        filename = save_to_file(data)

        # Github 업로드
        git_push(filename)

        # 1분 대기
        if i < 6:
            print("1분 대기 중...\n")
            time.sleep(60)

    print("\n===== 모든 작업 완료 =====")


# ------------------------------------------
# 코드 실행
# ------------------------------------------
if __name__ == "__main__":
    main_loop()
