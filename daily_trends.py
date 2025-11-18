import requests
from bs4 import BeautifulSoup
from datetime import datetime
from pathlib import Path


# -------------------------
# 1. HACKERNEWS (NIEUWSTE)
# -------------------------
def get_hackernews():
    url = "https://hn.algolia.com/api/v1/search_by_date?tags=story&hitsPerPage=5"
    r = requests.get(url, timeout=10).json()
    items = r.get("hits", [])[:3]

    return [
        {
            "source": "HackerNews",
            "title": item.get("title", "").strip(),
            "url": item.get("url") or ""
        }
        for item in items if item.get("title")
    ]


# -------------------------
# 2. TECHMEME HEADLINES
# -------------------------
def get_techmeme():
    url = "https://www.techmeme.com/"
    r = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=10)
    soup = BeautifulSoup(r.text, "html.parser")
    items = soup.select("strong a")[:3]

    return [
        {
            "source": "TechMeme",
            "title": item.text.strip(),
            "url": item.get("href")
        }
        for item in items
    ]


# -------------------------
# 3. PRODUCTHUNT (RSS)
# -------------------------
def get_producthunt():
    url = "https://www.producthunt.com/feed"
    r = requests.get(url, timeout=10)
    soup = BeautifulSoup(r.text, "xml")
    items = soup.find_all("item")[:3]

    return [
        {
            "source": "ProductHunt",
            "title": item.title.text.strip(),
            "url": item.link.text.strip()
        }
        for item in items
    ]


# -------------------------
# 4. GOOGLE NEWS TECH (RSS)
# -------------------------
def get_google_news():
    url = "https://news.google.com/rss/search?q=technology&hl=en-US&gl=US&ceid=US:en"
    r = requests.get(url, timeout=10)
    soup = BeautifulSoup(r.text, "xml")
    items = soup.find_all("item")[:3]

    return [
        {
            "source": "GoogleNews",
            "title": item.title.text.strip(),
            "url": item.link.text.strip()
        }
        for item in items
    ]


# -------------------------
# SAMENVATTING (3 ZINNEN)
# -------------------------
def summarize(trends):
    titles = [t["title"] for t in trends[:3]]
    while len(titles) < 3:
        titles.append("")

    s1 = f"Vandaag valt op: {titles[0]}."
    s2 = f"Daarnaast speelt: {titles[1]}."
    s3 = f"Verder belangrijk: {titles[2]}."

    return [s1, s2, s3]


# -------------------------
# HTML DASHBOARD BOUWEN
# -------------------------
def build_dashboard(trends, summaries):
    docs = Path("docs")
    docs.mkdir(exist_ok=True)

    html = Path("docs/index.html")
    today = datetime.utcnow().strftime("%Y-%m-%d")

    content = [
        "<!DOCTYPE html><html><head>",
        "<meta charset='UTF-8'/>",
        "<title>Daily Tech Trends</title>",
        "<style>",
        "body { background:#0f172a; color:#e2e8f0; font-family:Arial; padding:2rem; }",
        "h1 { color:#38bdf8; }",
        ".card{background:#1e293b;padding:1rem;margin:1rem 0;border-radius:12px;}",
        "a{color:#38bdf8;text-decoration:none;}",
        "</style></head><body>",
        f"<h1>🔥 Daily Tech Trends — {today}</h1>",
        "<h2>Samenvatting in 3 Zinnen</h2>",
    ]

    for s in summaries:
        content.append(f"<p>{s}</p>")

    content.append("<h2>Trends</h2>")

    for t in trends:
        content.append("<div class='card'>")
        content.append(f"<strong>{t['source']}:</strong><br>")
        content.append(f"<a href='{t['url']}'>{t['title']}</a>")
        content.append("</div>")

    content.append("</body></html>")
    html.write_text("\n".join(content), encoding="utf-8")


# -------------------------
# MAIN RUN
# -------------------------
if __name__ == "__main__":
    trends = []

    for f in (get_hackernews, get_techmeme, get_producthunt, get_google_news):
        try:
            trends += f()
        except Exception as e:
            print(f"Error in {f.__name__}: {e}")

    summaries = summarize(trends)
    build_dashboard(trends, summaries)

    print("\n🔥 DAILY SUMMARY:")
    for s in summaries:
        print("-", s)
