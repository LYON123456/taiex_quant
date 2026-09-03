"""
台指期歷史資料下載模組

資料來源：
  1. FinMind API（免費，有限額）：TaiwanFuturesDaily / TX
  2. yfinance 備用（Yahoo Finance TW=F）

用法：
  python data/fetch_data.py
  python data/fetch_data.py --source yfinance
  python data/fetch_data.py --start 2018-01-01
"""

import os
import sys
import argparse
import requests
import pandas as pd

# 讓腳本在任何目錄下執行都能正確 import config
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config

# ─────────────────────────────────────────
#  FinMind 下載
# ─────────────────────────────────────────


def fetch_from_finmind(
    start_date: str, end_date: str | None = None, token: str = ""
) -> pd.DataFrame:
    """
    從 FinMind API 下載台指期（TX）日線資料。

    Args:
        start_date: 開始日期，格式 YYYY-MM-DD
        end_date:   結束日期，None 表示到最新
        token:      FinMind API token（免費申請：https://finmindtrade.com/）

    Returns:
        DataFrame，欄位：datetime, open, high, low, close, volume, oi
    """
    params = {
        "dataset": config.FINMIND_DATASET,
        "data_id": config.FINMIND_DATA_ID,
        "start_date": start_date,
        "token": token,
    }
    if end_date:
        params["end_date"] = end_date

    print(f"[FinMind] 下載 {config.FINMIND_DATA_ID} 從 {start_date} ...")
    resp = requests.get(config.FINMIND_API_URL, params=params, timeout=30)
    resp.raise_for_status()
    data = resp.json()

    if data.get("status") != 200:
        raise RuntimeError(f"FinMind API 錯誤: {data.get('msg', '未知錯誤')}")

    df = pd.DataFrame(data["data"])
    if df.empty:
        raise ValueError("FinMind 回傳資料為空，請確認 token 或日期範圍")

    # 欄位對映
    # FinMind 欄位: date, contract_date, open, max, min, close, volume, open_interest
    rename_map = {
        "date": "datetime",
        "max": "high",
        "min": "low",
        "open_interest": "oi",
    }
    df = df.rename(columns=rename_map)

    # 只取近月合約（合約代碼最短的那個，即近月）
    if "contract_date" in df.columns:
        # 近月 = 當月或下月，取最近到期
        df["contract_date"] = df["contract_date"].astype(str)
        df = df.sort_values(["datetime", "contract_date"])
        df = df.groupby("datetime").first().reset_index()

    cols = ["datetime", "open", "high", "low", "close", "volume", "oi"]
    for col in cols:
        if col not in df.columns:
            df[col] = 0

    df = df[cols].copy()
    df["datetime"] = pd.to_datetime(df["datetime"])
    df = df.sort_values("datetime").reset_index(drop=True)

    # 轉為數值
    for col in ["open", "high", "low", "close", "volume", "oi"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    df = df.dropna(subset=["close"])
    print(
        f"[FinMind] 下載完成，共 {len(df)} 筆，日期範圍：{df['datetime'].min().date()} ~ {df['datetime'].max().date()}"
    )
    return df


# ─────────────────────────────────────────
#  yfinance 備用下載
# ─────────────────────────────────────────


def fetch_from_yfinance(start_date: str, end_date: str | None = None) -> pd.DataFrame:
    """
    從 Yahoo Finance 下載台指期資料（TW=F）。

    注意：Yahoo Finance 的台指期資料不含未平倉量（OI），
    oi 欄位將填 0，部分策略（OI 策略）需要真實 OI 資料才能運作。

    Args:
        start_date: 開始日期，格式 YYYY-MM-DD
        end_date:   結束日期，None 表示今天

    Returns:
        DataFrame，欄位：datetime, open, high, low, close, volume, oi
    """
    try:
        import yfinance as yf
    except ImportError:
        raise ImportError("請先安裝 yfinance：pip install yfinance")

    ticker = "TW=F"
    print(f"[yfinance] 下載 {ticker} 從 {start_date} ...")

    df = yf.download(ticker, start=start_date, end=end_date, progress=False)

    if df.empty:
        raise ValueError("yfinance 回傳資料為空")

    # yfinance 可能回傳 MultiIndex columns
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)

    df = df.reset_index()
    df = df.rename(
        columns={
            "Date": "datetime",
            "Open": "open",
            "High": "high",
            "Low": "low",
            "Close": "close",
            "Volume": "volume",
        }
    )

    df["oi"] = 0  # Yahoo Finance 無 OI 資料
    df["datetime"] = pd.to_datetime(df["datetime"])

    cols = ["datetime", "open", "high", "low", "close", "volume", "oi"]
    df = df[cols].sort_values("datetime").reset_index(drop=True)

    for col in ["open", "high", "low", "close", "volume"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    df = df.dropna(subset=["close"])
    print(
        f"[yfinance] 下載完成，共 {len(df)} 筆，日期範圍：{df['datetime'].min().date()} ~ {df['datetime'].max().date()}"
    )
    print("[yfinance] 注意：OI 欄位為 0，OI 策略將無法正常運作")
    return df


# ─────────────────────────────────────────
#  儲存 CSV
# ─────────────────────────────────────────


def save_csv(df: pd.DataFrame, path: str):
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    df.to_csv(path, index=False)
    print(f"[儲存] 資料已存至 {path}")


# ─────────────────────────────────────────
#  讀取本地 CSV
# ─────────────────────────────────────────


def load_csv(path: str) -> pd.DataFrame:
    """載入本地 CSV，並確保欄位正確。"""
    if not os.path.exists(path):
        raise FileNotFoundError(
            f"找不到資料檔：{path}\n請先執行 python data/fetch_data.py 下載資料"
        )

    df = pd.read_csv(path, parse_dates=["datetime"])
    df = df.sort_values("datetime").reset_index(drop=True)

    required_cols = ["datetime", "open", "high", "low", "close", "volume", "oi"]
    missing = [c for c in required_cols if c not in df.columns]
    if missing:
        raise ValueError(f"CSV 缺少欄位：{missing}")

    return df


# ─────────────────────────────────────────
#  Main
# ─────────────────────────────────────────


def main():
    parser = argparse.ArgumentParser(description="下載台指期歷史資料")
    parser.add_argument(
        "--source",
        choices=["finmind", "yfinance"],
        default="yfinance",
        help="資料來源（預設：yfinance，不需 token）",
    )
    parser.add_argument(
        "--start", default=config.DATA_START_DATE, help="開始日期 YYYY-MM-DD"
    )
    parser.add_argument(
        "--end", default=config.DATA_END_DATE, help="結束日期 YYYY-MM-DD"
    )
    parser.add_argument(
        "--token", default=config.FINMIND_TOKEN, help="FinMind API token"
    )
    parser.add_argument("--output", default=config.DATA_PATH, help="輸出 CSV 路徑")
    args = parser.parse_args()

    try:
        if args.source == "finmind":
            df = fetch_from_finmind(args.start, args.end, args.token)
        else:
            df = fetch_from_yfinance(args.start, args.end)

        save_csv(df, args.output)
        print("\n資料預覽（最後 5 筆）：")
        print(df.tail().to_string(index=False))

    except Exception as e:
        print(f"\n[錯誤] {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
