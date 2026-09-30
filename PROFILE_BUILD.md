# Profile maintenance and provenance

The current README is native Markdown with GitHub-supported HTML. Its text is
selectable; only the approved hero, three small SVG illustrations and existing
local Devicon icons are images. There is no README runtime dependency on CSS,
JavaScript, a server, an external card service or a contribution-snake workflow.

## Approved hero: installed and frozen

The final micro-polished files were copied byte-for-byte from the user-approved
hero-review staging directory on 30 September 2026. No hero generator was run.
`docs/hero-installation.json` contains the staged and installed SHA-256 hashes;
`hero-verification.json` records checks of the actual final repository assets.
These are installation checks, not the older staging reports.

Production README files:
- `assets/hero-cinematic.gif` / `assets/hero-cinematic.png`: 1440 × 560.
- `assets/hero-mobile.gif` / `assets/hero-mobile.png`: 720 × 1000.
- `assets/jarvis-morph.gif`: 480 × 560 standalone compatibility loop.

Sequence: Jaichandran → React → Node.js → MySQL → Java → Python → Jaichandran.
Each GIF has 78 frames: a 3-second portrait hold, five 2-second technology holds,
and six 600ms transitions (12 × 50ms). The complete loop is 16.6 seconds.
The final displayed logo sizes are React 288 × 257, Node.js 341 × 208,
MySQL 355 × 184, Java 355 × 176 and Python 256 × 246.

The portrait uses `assets/morph_stages/01_jaichandran.png`. Its original RGB pixels
are retained exactly in `assets/hero-source/jaichandran-cutout.png`; the aligned
`portrait-alpha.png` supplies transparency. This does not use the older compressed
portrait snapshot. The saved `gif-palettes.json` preserves the approved palettes.
The banner reference, raw portrait, Iron Man, Arc Reactor and every other original
source file remain untouched. Excluded artwork is not referenced by the current
README or its hero gallery.

The copied `scripts/build_hero.py`, cleaned logos, alpha mask and palettes preserve
the existing workflow for future explicitly approved changes. **Do not run the
hero generator against this repository.** Copy the approved bytes to restore the
hero; do not re-encode it. Existing obsolete review images remain unreferenced.

## Editing and previewing

Edit `README.md` directly. The previous rasterized `scripts/build_profile.py`
is retained for recovery, but its build entry point is disabled to protect this
native-text version. Legacy section PNGs remain intact and unused.

To refresh the complete local preview with GitHub's actual Markdown API:

```text
node scripts/render_preview.mjs
python scripts/verify_hero.py --source . --output .
python scripts/verify_profile.py . .
```

The render script needs network access and Node.js with fetch. The verification
scripts need Python, Pillow and NumPy. None invokes the hero generator.
Rendering sends the README to GitHub's Markdown endpoint; it does not publish,
commit or push. The returned HTML is retained in `docs/readme-rendered.html`.
`preview_readme.html` wraps that HTML in a local GitHub-like stylesheet.
`preview_morph.html` supplies local pause/play controls and the six formed stages.
Those controls are not part of the README.

The README selects mobile images at 600px or below, with static PNG sources first
for reduced-motion preferences. Empty alt text is intentional for decorative
lines and icons whose names appear directly beside them.

## Evidence and review scope

- `docs/CONTENT_EVIDENCE.md`: source basis and limits for each public claim.
- `docs/public-link-checks.json`: fresh repository and demo checks.
- `profile-verification.json`: source fingerprints and content decisions.
- `github-render-check.json`: GitHub Markdown API status, README hash and markup.
- `verification-results.json`: final references, image decoding and hero freeze.
- `docs/browser-verification.json`: desktop/mobile layout and playback checks.

Public repository activity is dated 30 September 2026. Do not relabel it live.
The ProjectPulse demo requires Vercel login and is deliberately omitted. LinkedIn
blocks automated requests; its exact profile URL is cross-linked from the public
GitHub profile. The email is retained from the user's existing README; delivery
has not been tested.

Education and training use user-supplied facts. No credential IDs, completion
dates, publications or presentation claims were added. Research numbers are
explicitly attributed to saved notebook output, not a new training run.

The full-page screenshots are local previews of the final README at desktop and
320/390/430px widths. They are not screenshots of a published GitHub profile.
The repository remains on its original branch with existing unrelated changes
preserved. No commit, push, deployment or publication was performed.
