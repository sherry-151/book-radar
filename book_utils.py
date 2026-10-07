"""書單整理：篩選、排序與 CSV 匯出。"""

import csv
import io
from pathlib import Path


def filter_books(books, keyword="", max_price=None, sort_by="rank"):
    """預算是每本書的最高售價；未知價格在設定預算時不列入。"""
    keyword = keyword.strip().casefold()
    result = []
    for book in books:
        if keyword and keyword not in book["title"].casefold():
            continue
        if max_price is not None:
            if book["price"] is None or book["price"] > max_price:
                continue
        result.append(book)
    if sort_by == "price":
        return sorted(result, key=lambda b: (
            b["price"] is None,
            b["price"] if b["price"] is not None else 0,
            b["rank"],
        ))
    return sorted(result, key=lambda b: b["rank"])


def export_csv(books, path):
    """utf-8-sig 讓 Excel 辨識中文字；無結果時也保留欄位名稱。"""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(csv_bytes(books))
    return path.resolve()


def csv_bytes(books):
    """供介面下載與檔案匯出共用，確保欄位一致。"""
    file = io.StringIO(newline="")
    writer = csv.writer(file)
    writer.writerow(["排名", "書名", "作者", "售價（新臺幣）", "商品連結"])
    for book in books:
            # 網頁文字以文字儲存，避免 Excel 將開頭符號當作公式。
            title = book["title"]
            author = book["author"]
            title = "'" + title if title.startswith(("=", "+", "-", "@")) else title
            author = "'" + author if author.startswith(("=", "+", "-", "@")) else author
            writer.writerow([book["rank"], title, author, book["price"], book["url"]])
    return file.getvalue().encode("utf-8-sig")
