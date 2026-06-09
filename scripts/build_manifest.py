"""
build_manifest.py — Scans news/ and summary/ directories and writes manifest.json.
Run from repo root: python scripts/build_manifest.py
Also executed automatically by GitHub Actions on push.
"""
import json
import os
import re
from pathlib import Path

BASE = Path(__file__).parent.parent


def extract_title(html_path: Path) -> str:
    try:
        text = html_path.read_text(encoding="utf-8", errors="ignore")[:3000]
        m = re.search(r"<title[^>]*>(.*?)</title>", text, re.IGNORECASE | re.DOTALL)
        if m:
            return re.sub(r"\s+", " ", m.group(1)).strip()
    except Exception:
        pass
    return html_path.stem


def find_hero(folder: Path) -> str | None:
    for f in sorted(folder.iterdir()):
        if "hero" in f.name.lower() and f.suffix.lower() == ".png":
            return f.relative_to(BASE).as_posix()
    return None


def scan_news(limit: int = 10) -> list[dict]:
    news_dir = BASE / "news"
    if not news_dir.exists():
        return []
    results = []
    folders = sorted(
        [d for d in news_dir.iterdir() if d.is_dir()],
        key=lambda d: d.name,
        reverse=True,
    )
    for folder in folders[:limit]:
        html_files = sorted(folder.glob("*.html"))
        if not html_files:
            continue
        html = html_files[0]
        results.append({
            "date": folder.name,
            "path": html.relative_to(BASE).as_posix(),
            "title": f"AI 情報日刊 — {folder.name}",
        })
    return results


def scan_summary(limit: int = 10) -> list[dict]:
    summary_dir = BASE / "summary"
    if not summary_dir.exists():
        return []
    results = []
    folders = sorted(
        [d for d in summary_dir.iterdir() if d.is_dir()],
        key=lambda d: d.name,
        reverse=True,
    )
    for folder in folders[:limit]:
        # Prefer *_magazine_brief.html, fall back to any .html
        html_files = sorted(folder.glob("*_magazine_brief.html"))
        if not html_files:
            html_files = sorted(folder.glob("*.html"))
        if not html_files:
            continue
        html = html_files[0]
        raw_date = folder.name[:8]  # YYYYMMDD
        date_fmt = f"{raw_date[:4]}-{raw_date[4:6]}-{raw_date[6:8]}"
        entry: dict = {
            "date": date_fmt,
            "path": html.relative_to(BASE).as_posix(),
            "title": extract_title(html),
        }
        hero = find_hero(folder)
        if hero:
            entry["hero"] = hero
        results.append(entry)
    return results


def main() -> None:
    manifest = {
        "news": scan_news(),
        "summary": scan_summary(),
    }
    out = BASE / "manifest.json"
    out.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    n = len(manifest["news"])
    s = len(manifest["summary"])
    print(f"manifest.json updated — {n} news, {s} summaries")


if __name__ == "__main__":
    main()
