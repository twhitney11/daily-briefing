#!/usr/bin/env python3
"""Run local Chromium desktop/mobile checks and simulated image-failure checks."""
import argparse
import functools
import http.server
import threading
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
p = argparse.ArgumentParser(description=__doc__)
p.add_argument('--screenshots', type=Path, default=Path('/tmp/daily-briefing-preview'))
args = p.parse_args(); args.screenshots.mkdir(parents=True, exist_ok=True)

class QuietHandler(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *args): pass

server = http.server.ThreadingHTTPServer(('127.0.0.1', 0), functools.partial(QuietHandler, directory=str(ROOT)))
threading.Thread(target=server.serve_forever, daemon=True).start()
base = f'http://127.0.0.1:{server.server_port}'
try:
    with sync_playwright() as pw:
        browser = pw.chromium.launch(executable_path='/usr/bin/chromium', headless=True, args=['--no-sandbox'])
        for width in [1440, 390, 320]:
            page = browser.new_page(viewport={'width': width, 'height': 1000}, device_scale_factor=1)
            errors = []; page.on('pageerror', lambda e: errors.append(str(e)))
            for filename in ['index.html', 'archive.html']:
                response = page.goto(f'{base}/{filename}', wait_until='networkidle')
                assert response.status == 200
                page.eval_on_selector_all('img', '(images) => images.forEach(i => i.loading = "eager")')
                page.locator('footer').scroll_into_view_if_needed()
                page.wait_for_function('Array.from(document.images).every(i => i.complete && i.naturalWidth > 0)')
                assert page.evaluate('document.documentElement.scrollWidth <= innerWidth'), (width, filename, 'overflow')
                if filename == 'index.html': assert page.locator('article').count() == 5
                assert not errors, errors
                page.screenshot(path=str(args.screenshots / f'{width}-{filename}.png'), full_page=True)
            page.close()
            print(f'PASS: {width}px latest/archive; no overflow, JS errors, or broken images')
        page = browser.new_page(viewport={'width': 390, 'height': 844})
        page.route('**/*.webp', lambda route: route.abort())
        page.goto(base + '/index.html', wait_until='networkidle')
        page.eval_on_selector_all('img', '(images) => images.forEach(i => i.loading = "eager")')
        page.locator('footer').scroll_into_view_if_needed()
        page.wait_for_function('Array.from(document.querySelectorAll("figure")).every(f => f.hidden)')
        assert page.locator('article').count() == 5
        assert page.locator('a.source').count() >= 5
        print('PASS: simulated image failures hide figures/captions; all five stories and sources remain')
        page.screenshot(path=str(args.screenshots / 'image-fallback.png'), full_page=True)
        browser.close()
finally:
    server.shutdown(); server.server_close()
