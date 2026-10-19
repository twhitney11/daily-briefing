#!/usr/bin/env python3
"""Render an explicitly dated edition and rebuild latest/archive. No network or AI API."""
import argparse
import json
import re
from datetime import date
from html import escape
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def link(url, label, css=''):
    if not url.startswith('https://'):
        raise ValueError('Sources must use HTTPS')
    return f'<a class="{css}" href="{escape(url, quote=True)}">{escape(label)}</a>'

def figure(item, hero=False):
    if not item:
        return ''
    path = ROOT / item['path']
    if not path.resolve().is_relative_to(ROOT) or not path.is_file():
        print(f"Image unavailable; omitting figure: {item['path']}")
        return ''
    if not item.get('alt') or not item.get('credit') or not item.get('rights'):
        raise ValueError('Image needs alt text, credit, and rights record')
    slot = item.get('panel')
    style = f' style="transform:translateX(-{slot * 20}%)"' if slot is not None else ''
    loading = 'eager' if hero else 'lazy'
    img = (f'<img src="{escape(item["path"], quote=True)}" alt="{escape(item["alt"], quote=True)}" '
           f'width="{item["width"]}" height="{item["height"]}" loading="{loading}" decoding="async"{style}>')
    if slot is not None:
        img = f'<div class="panel-window">{img}</div>'
    return f'<figure class="{"hero" if hero else "story-image"}">{img}<figcaption>{escape(item["credit"])}</figcaption></figure>'

def shell(title, body):
    css = (ROOT / 'templates/newspaper.css').read_text()
    return ('<!doctype html>\n<html lang="en"><head><meta charset="utf-8">'
            '<meta name="viewport" content="width=device-width,initial-scale=1">'
            f'<title>{escape(title)}</title><style>{css}</style>'
            '<script defer src="assets/image-fallback.js"></script></head><body>'
            '<a class="skip" href="#content">Skip to content</a>'
            f'<main class="paper" id="content">{body}</main></body></html>\n')

NAV = '<nav aria-label="Edition navigation"><a href="index.html">Latest edition</a><a href="archive.html">Edition archive</a></nav>'

def render(data):
    day = date.fromisoformat(data['date'])
    assert data['timezone'] == 'America/New_York'
    assert len(data['stories']) == 5, 'Exactly five stories required'
    header = (f'<header><div class="edition"><span>Independent daily digest</span>'
              f'<time datetime="{day}">{day.strftime("%A, %B")} {day.day}, {day.year}</time>'
              '<span>Five stories worth your time</span></div><h1>The Daily Curiosity</h1></header>')
    body = header + NAV + f'<p class="intro">{escape(data["intro"])}</p>' + figure(data.get('hero'), True)
    body += '<section class="stories" id="stories" aria-label="Five stories">'
    for n, s in enumerate(data['stories'], 1):
        assert 2 <= len(s['sentences']) <= 4
        assert s['sources'] and date.fromisoformat(s['news_date']) <= day
        body += (f'<article><div class="number">STORY {n:02d} · {escape(s["category"])}</div>'
                 f'<h2>{escape(s["headline"])}</h2>' + figure(s.get('image')) +
                 f'<p>{escape(" ".join(s["sentences"]))}</p>' +
                 f'<p class="story-date">Source published {escape(s["news_date"])} · Briefing date {day}</p>' +
                 '<div class="sources">' + ''.join(link(x['url'], x['label'] + ' ↗', 'source') for x in s['sources']) + '</div></article>')
    body += '</section><footer>Five sourced stories · Dates follow America/New_York. Generated illustrations are conceptual, not documentary images. Source links accompany every story.</footer>'
    return shell(f'The Daily Curiosity — {day}', body)

class Headline(HTMLParser):
    def __init__(self, text):
        super().__init__(); self.active = False; self.title = ''; self.done = False; self.feed(text)
    def handle_starttag(self, tag, attrs):
        if tag == 'h2' and not self.done: self.active = True
    def handle_endtag(self, tag):
        if tag == 'h2' and self.active: self.active = False; self.done = True
    def handle_data(self, text):
        if self.active: self.title += text

def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('date', help='Edition date YYYY-MM-DD in America/New_York')
    p.add_argument('--replace', action='store_true', help='Explicitly replace an existing edition after review')
    args = p.parse_args()
    day = date.fromisoformat(args.date).isoformat()
    data = json.loads((ROOT / f'editions/{day}.json').read_text())
    assert data['date'] == day
    target = ROOT / f'daily-briefing-{day}.html'
    html = render(data)
    if target.exists() and target.read_text() != html and not args.replace:
        raise SystemExit('Existing edition differs; inspect before using --replace')
    target.write_text(html)
    editions = sorted(ROOT.glob('daily-briefing-????-??-??.html'), reverse=True)
    (ROOT / 'index.html').write_bytes(editions[0].read_bytes())
    items = []
    for edition in editions:
        stamp = edition.stem[-10:]
        items.append(f'<li><a href="{edition.name}"><time datetime="{stamp}">{stamp}</time></a><p>{escape(Headline(edition.read_text()).title)}</p><span>5 stories</span></li>')
    archive = ('<header><div class="edition"><span>Independent daily digest</span><span>Browse by date</span></div><h1>The Daily Curiosity</h1></header>' + NAV +
               f'<h2>Edition archive</h2><p>{len(editions)} editions. {len(editions)*5} stories.</p><ul class="archive-list">' + ''.join(items) + '</ul><footer>Each edition retains its date and source links. Image credits appear alongside illustrations.</footer>')
    (ROOT / 'archive.html').write_text(shell('The Daily Curiosity — Edition archive', archive))
    print(f'Built {target.name}; latest {editions[0].name}; archive {len(editions)} editions')

if __name__ == '__main__': main()
