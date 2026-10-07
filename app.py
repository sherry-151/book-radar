"""執行方式：python -m streamlit run app.py"""

from datetime import datetime
import json
from pathlib import Path
from zoneinfo import ZoneInfo

import requests
import streamlit as st

from scraper import URL, parse_books
from book_utils import filter_books, csv_bytes


st.set_page_config(page_title="書單雷達", page_icon="📚", layout="wide")
st.title("📚 書單雷達")
st.write("整理暢銷書，用你的預算挑選下一本好書。")
st.caption("資料來源：金石堂中文書月排行榜｜查詢範圍：前 30 名")
st.link_button("查看原始排行榜", URL)

if st.button("取得／更新書單", type="primary"):
    try:
        with st.spinner("正在取得排行榜……"):
            response = requests.get(URL, timeout=20)
            response.raise_for_status()
            books = [b for b in parse_books(response.content) if b["rank"] <= 30]
            if not books:
                raise ValueError("沒有解析到書籍，來源頁面可能已改變。")
            st.session_state["books"] = books
            st.session_state["fetched_at"] = datetime.now(ZoneInfo("Asia/Taipei")).strftime("%Y-%m-%d %H:%M:%S")
            st.session_state["mode"] = "線上擷取"
        st.success(f"取得 {len(books)} 本書。")
    except (requests.RequestException, ValueError) as error:
        st.error(f"這次更新失敗：{error}")
        if "books" in st.session_state:
            st.info("下方仍顯示上一次取得的書單，請參考擷取時間。")

if st.button("載入離線範例書單"):
    try:
        path = Path(__file__).resolve().parent / "data" / "sample_books.json"
        sample = json.loads(path.read_text(encoding="utf-8"))
        st.session_state["books"] = sample["books"]
        st.session_state["fetched_at"] = sample["fetched_at"]
        st.session_state["mode"] = "離線範例"
    except (OSError, ValueError, KeyError) as error:
        st.error(f"範例載入失敗：{error}")

if "books" not in st.session_state:
    st.info("請按「取得／更新書單」，或載入離線範例，再設定搜尋條件。")
    st.stop()

st.caption(f"擷取時間（臺灣）：{st.session_state['fetched_at']}")
if st.session_state.get("mode") == "離線範例":
    st.warning("目前使用離線範例，書籍與價格是上述擷取時間的快照，不是最新資料。")
with st.sidebar:
    st.header("選書條件")
    keyword = st.text_input("書名關鍵字", placeholder="例如：臺灣")
    use_budget = st.checkbox("設定每本書的最高預算", value=True)
    budget = st.number_input("最高預算（新臺幣）", min_value=0, value=500, step=50, disabled=not use_budget)
    sort_label = st.selectbox("排序方式", ["排行榜順序", "價格由低到高"])
    st.caption("預算以每本書計算；設定預算時，沒有價格的書不列入結果。")

results = filter_books(
    st.session_state["books"], keyword,
    budget if use_budget else None,
    "price" if sort_label == "價格由低到高" else "rank",
)
st.subheader(f"符合條件：{len(results)} 本")
if results:
    rows = [{"排名": b["rank"], "書名": b["title"], "作者": b["author"],
             "售價（元）": b["price"], "商品連結": b["url"]} for b in results]
    st.dataframe(rows, hide_index=True, width="stretch", column_config={
        "商品連結": st.column_config.LinkColumn("商品連結", display_text="查看書籍"),
        "售價（元）": st.column_config.NumberColumn(format="NT$%d"),
    })
else:
    st.info("沒有符合條件的書籍，請更換關鍵字或提高預算。")
st.download_button("下載篩選書單 CSV", data=csv_bytes(results),
                   file_name="selected_books.csv", mime="text/csv")
st.caption("價格是擷取當下的頁面標價，實際購買請以書店結帳資訊為準。")
