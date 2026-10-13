#!/usr/bin/env python3
"""WordPress -> Hugo tek seferlik aktarım. Eski siteye sadece okuma isteği atar."""
import html, json, os, re, subprocess, sys, urllib.request
from urllib.parse import urlparse

SITE = os.environ.get("WP_SITE", "https://kemalbiyikli.com").rstrip("/")
HOST = urlparse(SITE).netloc
UA = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/126 Safari/537.36"}
OUT_POSTS, OUT_PAGES, STATIC = "content/posts", "content", "static"


def get(url):
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=60) as r:
        return r.read()


def api(path):
    items, page = [], 1
    while True:
        sep = "&" if "?" in path else "?"
        data = json.loads(get(f"{SITE}/wp-json/wp/v2/{path}{sep}per_page=100&page={page}"))
        items += data
        if len(data) < 100:
            return items
        page += 1


def terms(kind):
    return {t["id"]: html.unescape(t["name"]) for t in api(kind)}


def fetch_images(body):
    """wp-content/uploads altındaki görselleri indirir, linkleri göreli yapar (aynı yol korunur)."""
    pat = re.compile(r'(?:https?:)?//(?:www\.)?' + re.escape(HOST) + r'(/wp-content/uploads/[^"\'\s)>]+)')
    for path in set(pat.findall(body)):
        dest = os.path.join(STATIC, path.lstrip("/"))
        if not os.path.exists(dest):
            os.makedirs(os.path.dirname(dest), exist_ok=True)
            try:
                with open(dest, "wb") as f:
                    f.write(get(SITE + path))
                print("  img", path)
            except Exception as e:
                print("  IMG FAIL", path, e, file=sys.stderr)
    return pat.sub(r"\1", body)


def to_md(rendered):
    body = re.sub(r'\s(?:srcset|sizes)="[^"]*"', "", rendered)
    body = fetch_images(body)
    # Gutenberg kod bloklarındaki class'ları temizle
    body = re.sub(r'<pre[^>]*>', "<pre>", body)
    body = re.sub(r'<code(?: class="(?:language-)?([^"]*)")?>', lambda m: f'<code class="{m.group(1)}">' if m.group(1) else "<code class=\"text\">", body)
    md = subprocess.run(
        ["pandoc", "-f", "html", "-t", "gfm-raw_html", "--wrap=none"],
        input=body, capture_output=True, text=True, check=True,
    ).stdout
    # İç linkleri göreli yap
    md = re.sub(r"https?://(?:www\.)?" + re.escape(HOST) + r"(/[^)\s\"]*)", r"\1", md)
    return md.strip() + "\n"


def q(s):
    return json.dumps(s, ensure_ascii=False)


def front(d):
    lines = ["---"]
    for k, v in d.items():
        if v in (None, [], ""):
            continue
        lines.append(f"{k}: {q(v) if not isinstance(v, bool) else str(v).lower()}")
    lines.append("---\n")
    return "\n".join(lines)


def main():
    os.makedirs(OUT_POSTS, exist_ok=True)
    cats, tags = terms("categories"), terms("tags")
    posts = api("posts?status=publish")
    print(f"{len(posts)} yazı bulundu")
    for p in posts:
        title = html.unescape(p["title"]["rendered"])
        print("-", title)
        fm = {
            "title": title,
            "date": p["date"],
            "lastmod": p.get("modified"),
            "slug": p["slug"],
            "categories": [cats[c] for c in p.get("categories", []) if c in cats and cats[c] != "Uncategorized"],
            "tags": [tags[t] for t in p.get("tags", []) if t in tags],
            "draft": False,
        }
        with open(f"{OUT_POSTS}/{p['slug']}.md", "w", encoding="utf-8") as f:
            f.write(front(fm) + to_md(p["content"]["rendered"]))

    skip = {"home", "blog"}
    for p in api("pages?status=publish"):
        if p["slug"] in skip:
            continue
        title = html.unescape(p["title"]["rendered"])
        print("- sayfa:", title)
        fm = {"title": title, "url": f"/{p['slug']}/", "ShowReadingTime": False, "ShowToc": False}
        with open(f"{OUT_PAGES}/{p['slug']}.md", "w", encoding="utf-8") as f:
            f.write(front(fm) + to_md(p["content"]["rendered"]))
    print("Bitti.")


if __name__ == "__main__":
    main()
