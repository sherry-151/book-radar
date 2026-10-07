"""書單雷達：取得金石堂中文書月排行榜，展示前五本書。"""

import argparse
from pathlib import Path
from urllib.parse import urljoin, urlsplit
import requests
from bs4 import BeautifulSoup
from book_utils import filter_books, export_csv


URL = "https://www.kingstone.com.tw/bestseller/best/book?ranktype=m"


def parse_books(html):
    """用 CSS 選擇器解析書籍；同一商品只保留一次。"""
    soup = BeautifulSoup(html, "html.parser")
    books = []
    seen = set()
    for item in soup.select("li.modProList"):
        name = item.select_one(".modProName a")
        rank = item.select_one(".modProRank span")
        price = item.select_one(".priceset span:last-child b")
        author = item.select_one(".modProAuthor")
        if name is None or rank is None:
            continue
        link = urljoin(URL, name.get("href", ""))
        # 移除追蹤用查詢參數，讓相同商品的網址一致。
        parts = urlsplit(link)
        link = f"{parts.scheme}://{parts.netloc}{parts.path}"
        if link in seen:
            continue
        seen.add(link)
        rank_text = rank.get_text(strip=True)
        if not rank_text.isdigit():
            continue
        price_text = price.get_text(strip=True).replace(",", "") if price else ""
        books.append({
            "rank": int(rank_text),
            "title": name.get_text(strip=True),
            "author": author.get_text(" ", strip=True) if author else "未提供",
            "price": int(price_text) if price_text.isdigit() else None,
            "url": link,
        })
    return sorted(books, key=lambda book: book["rank"])


def main():
    parser = argparse.ArgumentParser(description="書單雷達：搜尋金石堂中文書月排行榜")
    parser.add_argument("--keyword", default="", help="書名包含的關鍵字")
    parser.add_argument("--budget", type=int, help="每本書的最高預算（新臺幣）")
    parser.add_argument("--sort", choices=["rank", "price"], default="rank", help="依排名或價格排序")
    args = parser.parse_args()
    if args.budget is not None and args.budget < 0:
        parser.error("預算不能是負數")
    print("正在連線到金石堂中文書月排行榜……")
    try:
        # timeout 避免網路沒有回應時無限等待。
        response = requests.get(URL, timeout=20)
        print(f"HTTP 狀態碼：{response.status_code}")

        if response.status_code == 403:
            print("網站拒絕這次請求，尚未取得書單。")
            print("這不是套件安裝錯誤；請先用瀏覽器查看來源頁面。")
            return

        response.raise_for_status()
        books = parse_books(response.content)
        if not books:
            print("沒有找到書籍資料，可能是頁面結構改變或回傳了其他頁面。")
            return
        # 基本版的查詢範圍限定在榜單前 30 名。
        books = [book for book in books if book["rank"] <= 30]
        print(f"取得榜單前 30 名中 {len(books)} 本書。")
        results = filter_books(books, args.keyword, args.budget, args.sort)
        print(f"符合條件：{len(results)} 本（關鍵字：{args.keyword or '不限'}；每本預算：{args.budget if args.budget is not None else '不限'}）")
        for book in results:
            price = f"NT${book['price']}" if book["price"] is not None else "未提供價格"
            print(f"\n第 {book['rank']} 名｜{book['title']}")
            print(f"作者：{book['author']}｜售價：{price}")
            print(book["url"])
        print("\n價格是擷取當下的頁面標價，實際購買請以書店結帳資訊為準。")
        if not results:
            print("沒有符合條件的書籍，可以提高預算或更換關鍵字。")
        path = Path(__file__).resolve().parent / "output" / "selected_books.csv"
        saved = export_csv(results, path)
        print(f"CSV 已儲存：{saved}")
        print("每次執行會更新同一份 CSV，想保留舊結果請先另存。")

    except requests.RequestException as error:
        print(f"連線未完成：{error}")
        print("請檢查網路連線，或稍後再試。")


if __name__ == "__main__":
    main()
