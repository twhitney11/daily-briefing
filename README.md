# The Daily Curiosity

A responsive, static newspaper archive. Published editions: October 8–21, 2026, with five original stories per edition.

GitHub Pages serves the root of `main`. Serving requires no dependencies or build step. `index.html` is the latest edition; `archive.html` links every dated page. New editions can be rendered from reviewed JSON with the included Python scripts.

Public editions omit personal references and images without established reuse rights. October 8–18 remain unchanged. October 19–21 add labeled native-generated editorial illustrations, locally stored and optimized, with source links and alt text.

See [the cloud publication procedure](docs/PUBLISHING.md) for research, generation, validation, image rights/fallbacks and publication. Run `python3 scripts/validate.py` and `python3 scripts/check_layout.py` before publication. Research and generation use native agent tools, not a separately billed API.

Unattended scheduling is not yet verified. This repository does not enable schedules; existing tasks are unchanged.
