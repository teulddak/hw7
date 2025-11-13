import yfinance as yf
import time
import subprocess
from datetime import datetime

# ============================
# 설정
# ============================

ticker = "373220.KS"   # LG에너지솔루션 야후 파이낸스 코드
target_dates = ["2025-11-11", "2025-06-04"]   # 가져올 날짜

repeat_count = 7        # 7번 실행
interval_sec = 60       # 1분(60초) 간격

# ============================
# 실행 반복
# ============================

for i in range(1, repeat_count + 1):
    print(f"\n===== 실행 {i}/{repeat_count} =====")

    # 야후 파이낸스 데이터 다운로드
    data = yf.download(ticker, start=min(target_dates), end=max(target_dates))

    # 파일 이름
    now = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    filename = f"stock_record_{now}.txt"

    with open(filename, "w", encoding="utf-8") as f:
        for d in target_dates:
            f.write(f"===== {d} =====\n")
            if d in data.index.strftime("%Y-%m-%d"):
                row = data.loc[data.index.strftime("%Y-%m-%d") == d]

                close = row["Close"].values[0]
                open_p = row["Open"].values[0]
                high = row["High"].values[0]
                low = row["Low"].values[0]
                volume = row["Volume"].values[0]

                f.write(f"시가: {open_p}\n")
                f.write(f"고가: {high}\n")
                f.write(f"저가: {low}\n")
                f.write(f"종가: {close}\n")
                f.write(f"거래량: {volume}\n\n")
            else:
                f.write("데이터 없음\n\n")

    # ============================
    # Git 자동 업로드
    # ============================
    subprocess.run(["git", "add", "."])
    subprocess.run(["git", "commit", "-m", f"자동 업로드: {filename}"])
    subprocess.run(["git", "push"])

    print(f"파일 업로드 완료 → {filename}")

    # 마지막 반복이면 쉬지 않음
    if i < repeat_count:
        time.sleep(interval_sec)
