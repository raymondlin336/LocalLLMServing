import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                    "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"}

def google_results(query: str, n: int = 5):
    # Organic results are usually under div.yuRUbf > a
    url = "https://www.google.com/search"
    params = {"q": query, "num": max(5, n)}
    r = requests.get(url, params=params, headers=UA, timeout=15)
    soup = BeautifulSoup(r.text, "html.parser")

    items = []
    for a in soup.select("div.yuRUbf > a")[:n]:
        title = a.get_text(strip=True)
        link = a.get("href")
        if title and link:
            items.append((title, link))
    return items

def web_search(query: str, n: int = 5) -> str:
    # Try Google first; if empty, fall back to DuckDuckGo
    results = google_results(query, n)

    if not results:
        return "No results found (blocked or HTML structure changed)."

    lines = []
    for i, (title, link) in enumerate(results, 1):
        lines.append(f"{i}. {title}\n   {link}")
    return "\n".join(lines)

# Example
print(web_search("tree", n=5))
