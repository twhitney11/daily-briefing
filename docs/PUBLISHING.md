# Cloud publication procedure

This is an agent-driven static publication workflow. Research and image generation
use the parent task's native tools. The Python scripts render and validate reviewed
content; they do not call an AI API or research on their own. No Mac, API key, paid
external image service, or background process is required by these scripts.
An unattended scheduled parent run has not yet been verified. Do not enable or
modify schedules as part of a publication run.

## 1. Start and inspect

Start the saved cloud environment and work in `/workspace/daily-briefing`. Read this
file, README, and any future AGENTS.md instructions. Inspect `git status` before
changing anything. Use `git fetch origin main` and compare HEAD with origin/main;
fast-forward a clean checkout when appropriate. Do not overwrite unrelated work.
The cloud checkout may be named `work`; publication targets remote `main` explicitly.
Get the edition date in `America/New_York`, not UTC:

```sh
TZ=America/New_York date +%F
```

If that dated edition already exists, inspect it and stop if already complete.
Do not silently replace a published edition or create duplicate archive entries.

## 2. Research and write

Read previous edition headlines to avoid repeats without a meaningful development.
Use native web search, then open the actual source pages. Select exactly five
varied, current, interesting stories across higher education/SUNY, AI,
cybersecurity/enterprise IT, science/space, gadgets, NY/North Country, cannabis,
and major US/world news. Do not force all categories into five stories.

Use primary sources where possible and reputable reporting for context. Check
publication dates, numerical claims, qualifications, and event status. An upcoming
launch is a target until a source confirms it happened. A proposal is not an enacted
policy. Explain uncertainty; avoid unsupported performance claims. Headlines and
2–4 original sentences per story should state the development and why it matters.
No private user information or personal references. Avoid long quotations.

Create `editions/YYYY-MM-DD.json` following the existing example. Each `sentences`
item is one complete sentence. Set `news_date` to the source publication date;
product listings can be current corroboration of a dated news story. Record source
verification and image decisions in a dated research note under `docs/`.

## 3. Images

Generate a thematic editorial hero using native `image_gen.imagegen`. Prefer real
article imagery for story figures only when the asset's reuse/embedding terms are
verified. Public access, an image credit, or presence on a government website does
not alone establish permission, especially for third-party artwork. Record the
source URL, creator, exact license/terms URL, date checked, permitted alterations,
and required credit. Honor download blocks; do not bypass restrictions or use a
proxy to acquire blocked assets. Never hotlink an expiring or unapproved URL.

When permission or access is unavailable, native generation can supply clearly
labeled conceptual illustrations. Do not depict an invented photograph, campus,
product, or mission design as real. A five-panel generated contact sheet can supply
five story figures via the `panel` indexes 0–4, avoiding five redundant downloads.
The current renderer expects five equal-width panels in one row, each about 1:2.
Omit `panel` for a normal photograph or standalone illustration.

The native tool saved PNG files under `/workspace/generated_images` in the manual
test. Confirm each actual path from its result; never assume a chat image is a
persisted file. Leave originals intact. Inspect the output, then optimize eligible
assets to a dated directory (Pillow is available in the tested environment):

```sh
python3 scripts/optimize_image.py /actual/generated/file.png assets/YYYY-MM-DD/hero.webp --width 1536
```

Only optimize third-party assets if their terms allow it. Use meaningful `alt`,
visible `credit`, dimensions, and `rights` in the JSON. Record generated provenance
and asset hashes. Avoid logos and misleading documentary imagery.

If native generation is unavailable, the output cannot be saved, or image rights
remain uncertain, set the relevant `hero`/`image` field to `null` and publish a
complete text edition. Missing local assets are omitted during rendering. The
small browser script hides a failed figure and caption without hiding the story.
This fallback must never turn into invented image credits or broken image URLs.

## 4. Render and validate

```sh
python3 scripts/build.py YYYY-MM-DD
python3 scripts/validate.py
python3 scripts/check_layout.py
git diff --check
git status --short
```

Build uses only Python's standard library. Image verification/optimization uses
Pillow; browser checks use Python Playwright and `/usr/bin/chromium`, all present
in the tested environment. If absent in a future environment, report the missing
check explicitly rather than claiming it passed. Browser screenshots default to
`/tmp/daily-briefing-preview` and should not be committed.

Inspect screenshots at 1440, 390, and 320 pixels. The browser check exercises actual
image decoding, overflow, JavaScript errors, and image-failure fallback. The
validator checks all editions, exactly five sourced articles, dates, local
navigation/fragments/assets, alt text, image decoding/size, latest equivalence,
and archive completeness. It does not fact-check prose or verify external URLs;
open every source using the native browser and record failures separately.

The renderer preserves dated HTML, writes only the requested edition, points
`index.html` at the newest edition, and rebuilds the archive from all dated pages.
`--replace` is required to change an existing edition; use it only for an intentional
reviewed revision. Confirm prior editions are unchanged in the diff. Update README
coverage dates when adding an edition. Review all staged files; exclude credentials,
private data, temporary screenshots, caches, and original oversized assets.

## 5. Publish and verify

With publication authorization, create one atomic commit containing the dated
page, latest, archive, JSON, and image assets (plus intentional procedure changes):

```sh
git add <explicit-reviewed-paths>
git diff --cached --check
git commit -m "Publish The Daily Curiosity for YYYY-MM-DD"
git push origin HEAD:refs/heads/main
git ls-remote origin refs/heads/main
```

Never force-push. If main advances, fetch and inspect the changes, reconcile locally,
rerun affected checks, and retry a normal fast-forward push. Do not retrieve tokens
or create credentials. The tested shell Git transport works through the configured
environment; `gh api` returned Forbidden. The native GitHub connector can read repo
metadata, refs and workflow runs without exposing credentials. Its tree/commit/ref
tools are an alternative atomic publication route, but this route must be verified
separately before relying on it for writes.

Read `repos/twhitney11/daily-briefing/actions/runs` through the GitHub connector.
Match `head_sha` to the new commit and require successful `pages build and deployment`.
Do not use the PR-filtered workflow wrapper to look for a direct-main Pages run.
Finally fetch the public latest, dated edition, archive, script and image URLs;
check date, links, image decoding and content hashes against the commit when possible.
If public reads are blocked, report the exact commit and successful deployment URL
and explicitly ask the parent to finish live-content verification. A successful
deployment is not proof of public content delivery or unattended scheduling.

Report the live URL, SHA, deployment status, image outcomes, checks and gaps.
Leave both existing tasks unchanged unless a separate instruction authorizes
scheduling changes.
