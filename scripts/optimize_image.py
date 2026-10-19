#!/usr/bin/env python3
"""Compress a generated/reuse-authorized image; never modify an archival source."""
import argparse
from pathlib import Path
from PIL import Image, ImageOps

p = argparse.ArgumentParser(description=__doc__)
p.add_argument('source', type=Path)
p.add_argument('destination', type=Path)
p.add_argument('--width', type=int, default=1600)
args = p.parse_args()
if args.source.resolve() == args.destination.resolve():
    raise SystemExit('Keep the source file intact')
with Image.open(args.source) as original:
    image = ImageOps.exif_transpose(original).convert('RGB')
    image.thumbnail((args.width, args.width * 4), Image.Resampling.LANCZOS)
    args.destination.parent.mkdir(parents=True, exist_ok=True)
    image.save(args.destination, 'WEBP', quality=82, method=6)
with Image.open(args.destination) as check:
    check.verify()
print(f'{args.destination}: {image.width}x{image.height}, {args.destination.stat().st_size:,} bytes')
