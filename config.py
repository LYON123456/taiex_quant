# ============================================================
# 台指期量化回測系統 - 系統設定
# ============================================================

# 資金設定
INITIAL_CASH = 1_000_000      # 初始資金 100 萬
COMMISSION = 0.0000425        # 手續費（台指期約 50 元/口，合約值約 120萬，約 0.004%）
SLIPPAGE = 1                  # 滑價（點）

# 台指期合約規格
CONTRACT_MULTIPLIER = 200     # 一點 = 200 元
MIN_MARGIN = 83_000           # 原始保證金（元）

# 策略參數 - 均線策略
MA_FAST = 20
MA_SLOW = 60

# 策略參數 - ATR
ATR_PERIOD = 14
ATR_MULTIPLIER = 1.5          # 停損倍數

# 策略參數 - 成交量
VOLUME_MA_PERIOD = 20
VOLUME_MULTIPLIER = 2.0       # 成交量突破倍數

# 策略參數 - 未平倉量（OI）
OI_CHANGE_THRESHOLD = 0.02    # OI 增加 2% 視為主力進場
OI_MA_PERIOD = 5

# 融合策略參數
COMBINED_VOLUME_MULTIPLIER = 1.5   # 融合策略成交量門檻（較寬鬆）

# RSI 參數
RSI_PERIOD = 14
RSI_OVERBOUGHT = 70
RSI_OVERSOLD = 30

# 資料設定
DATA_PATH = "data/taiex_futures.csv"
DATA_START_DATE = "2020-01-01"
DATA_END_DATE = None          # None 表示到最新

# FinMind API 設定
FINMIND_API_URL = "https://api.finmindtrade.com/api/v4/data"
FINMIND_DATASET = "TaiwanFuturesDaily"
FINMIND_DATA_ID = "TX"       # 台指期近月
FINMIND_TOKEN = ""            # 填入你的 FinMind token（免費申請）

# 回測結果輸出
REPORT_DIR = "report"
