#!/usr/bin/env python3
"""Check every edition, local navigation, image files, and latest/archive consistency."""
import json
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[1]

class Page(HTMLParser):
    def __init__(self, text):
        super().__init__(); self.articles = []; self.current = None
        self.links = []; self.assets = []; self.images = []; self.ids = set(); self.dates = []
        self.feed(text)
    def handle_starttag(self, tag, attrs):
        d = dict(attrs)
        if tag == 'article': self.current = []; self.articles.append(self.current)
        if d.get('id'): self.ids.add(d['id'])
        if tag == 'time': self.dates.append(d.get('datetime'))
        if tag == 'a':
            self.links.append(d.get('href', ''))
            if self.current is not None and 'source' in d.get('class', '').split():
                self.current.append(d.get('href', ''))
        if tag in ['img', 'script'] and 'src' in d: self.assets.append(d['src'])
        if tag == 'img': self.images.append(d)
    def handle_endtag(self, tag):
        if tag == 'article': self.current = None

def main():
    pages = {p.name: Page(p.read_text()) for p in ROOT.glob('*.html')}
    editions = sorted(ROOT.glob('daily-briefing-????-??-??.html'))
    assert editions, 'No editions'
    for path in editions:
        page = pages[path.name]
        assert len(page.articles) == 5 and all(page.articles), path.name
        assert path.stem[-10:] in page.dates, path.name
        for sources in page.articles:
            assert all(urlsplit(u).scheme == 'https' for u in sources), path.name
    checked_images = set()
    for name, page in pages.items():
        for href in page.links + page.assets:
            url = urlsplit(href)
            if url.scheme or url.netloc: continue
            target = ROOT / (unquote(url.path) or name)
            assert target.resolve().is_relative_to(ROOT) and target.is_file(), (name, href)
            if url.fragment and target.suffix == '.html':
                assert url.fragment in pages[target.name].ids, (name, href)
        for img in page.images:
            assert img.get('alt', '').strip(), (name, 'missing alt')
            assert int(img['width']) > 0 and int(img['height']) > 0
            assert not urlsplit(img['src']).scheme, 'Images must be persisted locally'
            checked_images.add(img['src'])
    if checked_images:
        from PIL import Image
        for src in checked_images:
            with Image.open(ROOT / src) as image: image.verify()
            assert (ROOT / src).stat().st_size < 1_000_000, 'Optimize large image: ' + src
    assert (ROOT / 'index.html').read_bytes() == editions[-1].read_bytes()
    archive_links = pages['archive.html'].links
    assert all(archive_links.count(p.name) == 1 for p in editions)
    assert len([u for u in archive_links if u.startswith('daily-briefing-')]) == len(editions)
    for path in (ROOT / 'editions').glob('*.json'):
        data = json.loads(path.read_text())
        assert data['timezone'] == 'America/New_York' and len(data['stories']) == 5
        assert all(2 <= len(s['sentences']) <= 4 for s in data['stories'])
        images = [data.get('hero')] + [s.get('image') for s in data['stories']]
        for image in filter(None, images):
            assert image.get('rights') and image.get('credit') and image.get('alt')
    print(f'PASS: {len(editions)} editions / {len(editions)*5} sourced stories; local links, fragments, dates, latest/archive, {len(checked_images)} decoded image files, alt text and rights records')

if __name__ == '__main__': main()
