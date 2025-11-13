import yfinance as yf
import time
import subprocess
from datetime import datetime

# ===========================================
# 🔥 설정 파트
# ===========================================
ticker = "373220.KS"  # LG에너지솔루션(한국 야후 티커)
target_dates = ["20250604", "20251111"]  # 주인님이 원하는 과거 날짜 목록

# 야후 날짜 변환 (YYYYMMDD → YYYY-MM-DD)
def convert_date(d):
    return f"{d[:4]}-{d[4:6]}-{d[6:8]}"

# 범위 계산
start = convert_date(min(target_dates))
end = convert_date(max(target_dates))

# ===========================================
# 🔥 7번 반복 실행
# ===========================================
for run in range(1, 8):
    print(f"\n===== 실행 {run}/7 =====")

    # ===========================================
    # 🔥 야후 데이터 다운로드
    # ===========================================
    df = yf.download(ticker, start=start, end=end)

    if df.empty:
        print("❌ 야후 데이터 다운로드 실패")
    else:
        print("✅ 야후 데이터 다운로드 성공")

    # 인덱스를 'YYYYMMDD' 형식으로 맞춤
    df.index = df.index.strftime("%Y%m%d")

    # ===========================================
    # 🔥 요청 날짜만 추출
    # ===========================================
    results = {}

    for d in target_dates:
        if d in df.index:
            row = df.loc[d]
            results[d] = {
                "시가": float(row["Open"]),
                "고가": float(row["High"]),
                "저가": float(row["Low"]),
                "종가": float(row["Close"]),
                "거래량": int(row["Volume"])
            }
        else:
            results[d] = "데이터 없음"

    # ===========================================
    # 🔥 파일로 저장
    # ===========================================
    filename = f"stock_record_run{run}.txt"

    with open(filename, "w", encoding="utf-8") as f:
        f.write("======= 과거 데이터 (야후) =======\n\n")
        for d in target_dates:
            f.write(f"날짜: {d}\n")
            if results[d] == "데이터 없음":
                f.write("데이터 없음\n\n")
            else:
                f.write(f"시가: {results[d]['시가']:,}\n")
                f.write(f"고가: {results[d]['고가']:,}\n")
                f.write(f"저가: {results[d]['저가']:,}\n")
                f.write(f"종가: {results[d]['종가']:,}\n")
                f.write(f"거래량: {results[d]['거래량']:,}\n\n")

    print(f"📄 파일 생성됨 → {filename}")

    # ===========================================
    # 🔥 GitHub 자동 업로드
    # ===========================================
    subprocess.run(["git", "add", "."])
    subprocess.run(["git", "commit", "-m", f"자동 업로드: {filename}"])
    subprocess.run(["git", "push"])

    print(f"📌 업로드 완료 → {filename}")

    # ===========================================
    # 🔥 다음 실행까지 1분 대기
    # ===========================================
    if run < 7:
        print("⏳ 1분 대기 중...\n")
        time.sleep(60)

print("\n===== 전체 완료되었습니다 주인님! =====")
