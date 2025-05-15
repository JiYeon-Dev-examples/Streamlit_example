#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import datetime
import re
import requests
import feedparser
import pandas as pd
import win32com.client as win32
from bs4 import BeautifulSoup
from fastapi import FastAPI
from apscheduler.schedulers.asyncio import AsyncIOScheduler

# ————————————— 설정 및 유틸 —————————————
HEADERS = {"User-Agent": "Mozilla/5.0"}

def to_html_table(data, columns):
    html = ['<table style="width:700px; table-layout:fixed; '
            'border-collapse:collapse; '
            'font-family:\'Malgun Gothic\',sans-serif; '
            'font-size:0.95em; '
            'margin:0.5em 0 0.5em 2em;">']
    html.append('<colgroup>')
    for i in range(len(columns)):
        col_width = '25%' if i == 0 else f'{75//(len(columns)-1)}%'
        html.append(f'<col style="width:{col_width};">')
    html.append('</colgroup>')
    html.append('<tr>')
    for i, col in enumerate(columns):
        col_width = '25%' if i == 0 else f'{75//(len(columns)-1)}%'
        html.append(
            f'<th style="border:1px solid #ddd; padding:10px 8px; '
            f'text-align:center; font-family:\'Malgun Gothic\',sans-serif; '
            f'font-size:0.95em; width:{col_width};">{col}</th>'
        )
    html.append('</tr>')
    for row in data:
        html.append('<tr>')
        for col in columns:
            html.append(
                f'<td style="border:1px solid #ddd; padding:10px 8px; '
                f'text-align:center; font-family:\'Malgun Gothic\',sans-serif; '
                f'font-size:0.95em;">{row.get(col, "")}</td>'
            )
        html.append('</tr>')
    html.append('</table>')
    return "\n".join(html)

def fetch_ruliweb_articles(top_n=5):
    url = "https://bbs.ruliweb.com/news/523/rss"
    resp = requests.get(url, headers=HEADERS)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.content, "xml")
    items = soup.find_all("item")[:top_n]
    return [
        {"title": it.title.get_text(strip=True), "link": it.link.get_text(strip=True)}
        for it in items
    ]

def fetch_vgc_platform_articles(slug, top_n=2):
    url = f"https://www.videogameschronicle.com/platforms/{slug}/"
    resp = requests.get(url, headers=HEADERS)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")
    out = []
    for art in soup.find_all("article"):
        title = link = None
        for a in art.find_all("a", href=True):
            href, txt = a["href"], a.get_text(strip=True)
            if "/news/" in href and "/page/" not in href and not txt.isdigit():
                title, link = txt, href
                break
        if not title:
            continue
        summary = art.find("p").get_text(strip=True) if art.find("p") else ""
        out.append({"title": title, "summary": summary, "link": link})
        if len(out) >= top_n:
            break
    return out

def fetch_gamesindustry_html(top_n=2):
    feed = feedparser.parse("https://www.gamesindustry.biz/feed")
    return [
        {"title": e.title, "summary": "", "link": e.link}
        for e in feed.entries[:top_n]
    ]

def fetch_global_topsellers(top_n=5):
    url = "https://store.steampowered.com/search/?filter=globaltopsellers"
    resp = requests.get(url, headers=HEADERS)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")
    rows = soup.select(".search_result_row")[:top_n]
    return [
        {"Rank": idx, "Title": r.select_one(".title").get_text(strip=True)}
        for idx, r in enumerate(rows, start=1)
    ]

def fetch_popular_upcoming(top_n=5):
    url = "https://store.steampowered.com/search/?filter=popularcomingsoon"
    resp = requests.get(url, headers=HEADERS)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")
    out = []
    for r in soup.select(".search_result_row")[:top_n]:
        out.append({
            "Title":   r.select_one(".title").get_text(strip=True),
            "Release": r.select_one(".search_released").get_text(strip=True)
        })
    return out

def fetch_upcoming_releases_df(url):
    resp = requests.get(url, headers=HEADERS)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")
    rec = []
    for p in soup.find_all("p"):
        lines = [
            ln.strip() for ln in p.get_text("\n", strip=True).split("\n")
            if ln.strip()
        ]
        if len(lines) < 2 or not re.match(r"^\d{2}월\s*\d{2}일", lines[0]):
            continue
        date, title = lines[0], lines[1]
        parts = [x.strip() for x in (lines[2] if len(lines) > 2 else "").split("|")]
        rec.append({
            "발매일": date,
            "게임명": title,
            "플랫폼": parts[0] if len(parts) > 0 else "",
            "장르": parts[1] if len(parts) > 1 else "",
            "한국어 지원 여부": parts[2] if len(parts) > 2 else ""
        })
    return pd.DataFrame(rec)

def render_section(header, emoji, arts, hide_summary=False):
    parts = [
        f'<h2 style="font-family:Calibri; font-size:1.1em; '
        f'font-weight:bold; margin-top:1em; margin-bottom:0.5em;">'
        f'[{emoji} {header}]</h2>'
    ]
    for art in arts:
        parts.append(
            f'<h3 style="font-family:Calibri; font-size:1.2em; '
            f'font-weight:bold; color:#196F92; margin:0.2em 0;">'
            f'· {art["title"]}</h3>'
        )
        if not hide_summary and art.get("summary"):
            parts.append(
                f'<p style="font-family:Calibri; margin:0 0 0.5em 1.5em;">'
                f'{art["summary"]}</p>'
            )
        parts.append(
            f'<p style="font-family:Calibri; margin:0 0 1em 1.5em;">'
            f'<a href="{art["link"]}" style="text-decoration:underline;">'
            f'Learn More →</a></p>'
        )
    return "\n".join(parts)

def send_weekly_mail():
    now     = datetime.datetime.now()
    date_str = now.strftime("%Y-%m-%d")
    subject = f"Daily Gaming & Industry News ({date_str})"

    # 배너
    banner_html = f'''
    <table cellpadding="0" cellspacing="0" border="0"
           style="width:1200px; margin:0 0 1em 0; font-family:Calibri;">
      <tr style="background-color:#000; color:#fff;">
        <td style="padding:8px 12px; font-size:1.2em; font-weight:bold; text-align:left;">
          DAILY GAMING &amp; INDUSTRY NEWS
        </td>
        <td style="padding:8px 12px; font-size:1em; text-align:right;">
          {date_str}
        </td>
      </tr>
    </table>
    '''
    html_parts = [banner_html, '<div style="font-family:Calibri;">']

    # 국내 뉴스
    ruli = fetch_ruliweb_articles(5)
    html_parts.append(
        '<h2 style="font-family:Calibri; font-size:1.4em; '
        'font-weight:bold; margin-bottom:0.5em;">'
        'Weekly News Highlights: 국내</h2>'
    )
    for art in ruli:
        html_parts.append(
            f'<h3 style="font-family:\'Malgun Gothic\',sans-serif; '
            f'font-size:1em; font-weight:bold; color:#196F92; '
            f'margin:0.2em 0;">· {art["title"]}</h3>'
        )
        html_parts.append(
            f'<p style="font-family:\'Malgun Gothic\',sans-serif; '
            f'font-size:0.9em; margin:0 0 1em 1.5em;">'
            f'<a href="{art["link"]}" style="text-decoration:underline;">'
            f'자세히 보기 →</a></p>'
        )

    # 해외 뉴스
    html_parts.append('<hr style="border:none; border-top:1px solid #ccc; margin:2em 0;">')
    html_parts.append(
        '<h2 style="font-family:Calibri; font-size:1.4em; '
        'font-weight:bold; margin-bottom:0.5em;">'
        'Weekly News Highlights: 해외</h2>'
    )
    html_parts.append('<div style="margin-left:2em;">')
    for title, emoji, slug in [
        ("Playstation/Xbox/PC Gaming", "🎮", "playstation"),
        ("Nintendo",               "🍄", "nintendo"),
        ("Mobile",                 "📱", "mobile")
    ]:
        html_parts.append(render_section(title, emoji, fetch_vgc_platform_articles(slug,2)))
    html_parts.append('</div>')

    # SteamDB 차트
    html_parts.append('<hr style="border:none; border-top:1px solid #ccc; margin:2em 0;">')
    html_parts.append('<div style="margin-left:2em;">')
    html_parts.append(
        '<h2 style="font-family:Calibri; font-size:1.4em; '
        'font-weight:bold; margin-bottom:0.5em;">Steam Sales Trend</h2>'
    )
    html_parts.append('<div style="margin-left:2em;">')
    html_parts.append(to_html_table(fetch_global_topsellers(5), ["Rank","Title"]))
    html_parts.append(to_html_table(fetch_popular_upcoming(5), ["Title","Release"]))
    html_parts.append('</div></div>')

    # Upcoming Game Releases
    html_parts.append('<hr style="border:none; border-top:1px solid #ccc; margin:2em 0;">')
    html_parts.append(
        '<h2 style="font-family:Calibri; font-size:1.4em; '
        'font-weight:bold; margin-top:1em; margin-bottom:0.5em;">'
        '🆕 Upcoming Game Releases on May</h2>'
    )
    html_parts.append(
        '<p style="font-family:\'Malgun Gothic\',sans-serif; '
        'font-size:0.8em; margin:0 0 0.5em 2em; font-style:italic;">'
        '* 해당 내용은 루리웹 안민균 기자님의 월별 신작 소개 기사에서 발췌하였습니다.'
        '</p>'
    )
    df_up = fetch_upcoming_releases_df("https://bbs.ruliweb.com/news/read/210211")
    html_parts.append(to_html_table(
        df_up.to_dict("records"),
        ["발매일","게임명","플랫폼","장르","한국어 지원 여부"]
    ))
    html_parts.append('<hr style="border:none; border-top:1px solid #ccc; margin:2em 0;">')

    html_parts.append('</div>')
    html_body = "\n".join(html_parts)

    outlook = win32.Dispatch("Outlook.Application")
    mail    = outlook.CreateItem(0)
    mail.To       = "claireryu@nexon.co.kr; castle181@naver.com"
    mail.Subject  = subject
    mail.HTMLBody = html_body
    mail.Send()

app = FastAPI()
scheduler = AsyncIOScheduler(timezone="Asia/Seoul")

@app.on_event("startup")
async def start_scheduler():
    scheduler.add_job(
        send_weekly_mail, 'cron', 
        day_of_week='mon',
        hour=9, 
        minute=20
    )
    scheduler.start()

@app.get("/health")
async def health():
    return {"status": "ok"}

# Run with:
# uvicorn main:app --reload

