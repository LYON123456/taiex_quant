# taiex_quant — 已合併至 twstock_googlesheet

此 repo 已於 2026-04-26 完成合併。

## 合併目標

程式碼已整合至：[twstock_googlesheet](../twstock_googlesheet)

| 原始檔案 | 合併後位置 |
|---------|-----------|
| `config.py` | `app/services/futures/taiex_config.py` |
| `data/fetch_data.py` | `app/services/futures/taiex_data_fetcher.py` |
| `data/README.md` | `docs/` (參考) |
| `backtest/`, `indicators/`, `strategy/` | `app/services/futures/` (骨架已建立) |

## 使用方式

請至 `twstock_googlesheet` 操作：
```bash
# 下載台指期日線資料
python scripts/fetch_taiex_daily.py
python scripts/fetch_taiex_daily.py --source finmind --token YOUR_TOKEN

# 執行回測 API
# POST http://localhost:8000/api/v1/taiex-backtest/run
```

此 repo 保留供歷史參考，不再主動維護。
