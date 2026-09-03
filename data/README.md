# 資料目錄

## 資料來源

### 方案一：FinMind（推薦，含 OI 資料）

FinMind 提供完整的台指期日線資料，包含未平倉量（OI），適合執行所有策略。

1. 前往 https://finmindtrade.com/ 免費註冊取得 token
2. 將 token 填入 `config.py` 的 `FINMIND_TOKEN`
3. 執行下載：

```bash
python data/fetch_data.py --source finmind --token YOUR_TOKEN
```

### 方案二：Yahoo Finance（不需 token，但無 OI）

```bash
python data/fetch_data.py --source yfinance
```

注意：Yahoo Finance 的台指期（TW=F）不含未平倉量（OI），
使用此方案時 OI 策略（oi_strategy）將無法正常運作。

## 資料格式

`taiex_futures.csv` 欄位：

| 欄位     | 說明           | 範例       |
|----------|----------------|------------|
| datetime | 交易日期       | 2020-01-02 |
| open     | 開盤價（點）   | 12000      |
| high     | 最高價（點）   | 12050      |
| low      | 最低價（點）   | 11980      |
| close    | 收盤價（點）   | 12030      |
| volume   | 成交量（口）   | 45000      |
| oi       | 未平倉量（口） | 89000      |

## 注意事項

- 台指期為近月合約（TX），每月第三個星期三到期換約
- 換約日前後可能有跳空，屬正常現象
- 建議使用 2020 年以後的資料，流動性較佳
