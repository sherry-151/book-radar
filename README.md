# 書單雷達：暢銷書整理與預算選書工具

Python 課程期末專題。整理金石堂中文書月排行榜前 30 名，讓使用者依書名關鍵字與每本書的預算選書，並下載 CSV。

## 功能

- 手動取得排行榜、去除重複商品，保留來源排名。
- 書名關鍵字搜尋、每本書最高預算篩選。
- 按排名或價格由低到高排序。
- 匯出含 UTF-8 BOM 的 CSV，方便 Excel 辨識中文。
- 載入附有擷取時間的真實資料快照，供離線練習與展示。

## 安裝與執行

已在 macOS、Python 3.14 環境驗證。

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

Windows 的啟用指令為 `.venv\Scripts\activate`（命令提示字元）。啟動後開啟終端機顯示的本機網址，通常是 http://localhost:8501。這是本機程式，並未部署成公開網站。

## 操作

1. 按「取得／更新書單」，或按「載入離線範例書單」。
2. 在側欄設定書名關鍵字、預算與排序。文字輸入後按 Enter。
3. 按「下載篩選書單 CSV」。下載內容與篩選結果一致。

命令列也可以使用：

```bash
python scraper.py --budget 300 --sort price
python scraper.py --keyword "臺灣" --budget 500
```

命令列輸出存於 `output/selected_books.csv`，每次執行會覆蓋。介面下載不會覆蓋這個檔案。

## 程式結構

- `scraper.py`：HTTP 請求、CSS 選擇器解析、去重與命令列入口。
- `book_utils.py`：搜尋、預算判斷、排序、CSV 編碼。
- `app.py`：Streamlit 操作介面、錯誤提示與離線模式。
- `data/sample_books.json`：真實排行榜快照與擷取時間。
- `docs/demo_script.md`：約六分鐘的錄影流程與講稿。

流程：取得 HTML → 解析書籍欄位 → 清理價格與重複商品 → 篩選排序 → 顯示／匯出。

## 資料來源與限制

[金石堂中文書月排行榜](https://www.kingstone.com.tw/bestseller/best/book?ranktype=m)。原先試用博客來時收到 HTTP 403，實際作品改用可取得頁面資料的金石堂。

- 只涵蓋榜單前 30 名，未搜尋全站，也未跨店比價。
- 排名來自書店，不代表全臺銷售排名。
- 價格為擷取時頁面標價，購買以書店結帳資訊為準。
- 缺少價格的書在設定預算時不列入；未設預算時可顯示。
- 關鍵字採文字包含比對，「台」與「臺」目前不同。
- 網頁結構改變、拒絕請求或網路中斷可能讓更新失敗。離線模式有明確標示；更新失敗時保留舊資料與原擷取時間。
- 每次手動更新只請求排行榜一頁，沒有持續自動輪詢。教材投影片未包含在此專案中。

## 驗證

已驗證預算邊界、缺價排除、關鍵字與空結果、價格排序、CSV 中文往返，以及介面篩選流程。Excel 實際開啟結果由使用者確認。

## Demo

YouTube 連結：錄製完成後補上。

## 學習與致謝

延伸課堂的 Requests 與 HTML 解析練習，加入資料清理與操作介面。開發過程使用 AI 協助撰寫與除錯，提交者應理解並能解說核心程式。
