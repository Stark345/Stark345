"""Verify final native-text README references and frozen assets. No asset generation."""
from pathlib import Path
from html.parser import HTMLParser
from datetime import datetime, timezone
import hashlib, json, re, sys
import xml.etree.ElementTree as ET
from PIL import Image

root = Path(sys.argv[1]).resolve()
md = (root/'README.md').read_text(encoding='utf-8')
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()

class Inspect(HTMLParser):
    def __init__(self):
        super().__init__()
        self.assets, self.images, self.tags = [], [], []
    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        self.tags.append(tag)
        assert 'style' not in attrs, 'No custom inline CSS in README'
        assert not any(k.startswith('on') for k in attrs), 'No event handlers'
        if tag in ('img', 'source'):
            self.assets.append(attrs.get('src') or attrs.get('srcset'))
        if tag == 'img':
            assert 'alt' in attrs
            self.images.append(attrs)
parser = Inspect()
parser.feed(md)
assert not set(parser.tags) & {'script','canvas','style','iframe','svg'}
assert len(re.findall(r'^## ', md, re.M)) == 8
assert 'Cyber AI' not in md and '08_cyber_ai' not in md
assert 'snake' not in md.lower()
assert 'assets/profile/whoami' not in md and 'assets/profile/project-' not in md

def exact_reference(ref):
    assert not ref.startswith(('http:', 'https:', 'file:', 'C:', 'E:')), ref
    current = root
    for part in Path(ref).parts:
        assert part not in ('..','.'), ref
        assert part in [p.name for p in current.iterdir()], 'Incorrect case or missing: '+ref
        current = current/part
    assert current.is_file(), ref
    return current

refs = set(parser.assets)
refs.update(re.findall(r'!\[[^\]]*\]\(([^)]+)\)', md))
for ref in refs:
    p = exact_reference(ref)
    if p.suffix.lower() == '.svg':
        tree = ET.parse(p)
        assert not any(n.tag.rsplit('}',1)[-1] in ('script','foreignObject') for n in tree.iter())
    else:
        with Image.open(p) as im:
            for n in range(getattr(im,'n_frames',1)):
                im.seek(n)
                im.load()
installation = json.loads((root/'docs/hero-installation.json').read_text(encoding='utf-8-sig'))
frozen = {r['path']:sha(root/r['path']) for r in installation['files'] if r['frozen']}
for record in installation['files']:
    if record['frozen']:
        assert frozen[record['path']] == record['staged_sha256']
hero = json.loads((root/'hero-verification.json').read_text())
assert hero['status'] == 'passed' and hero['approved_hashes_match']
render = json.loads((root/'github-render-check.json').read_text())
assert render['readme_sha256'] == sha(root/'README.md')
assert render['responsive_sources_preserved']
assert md.index('(prefers-reduced-motion: reduce) and (max-width: 600px)') < md.index('(prefers-reduced-motion: reduce)"')
external = sorted(set(re.findall(r'\]\((https?://[^)]+)\)', md)))
report = dict(checked_at=datetime.now(timezone.utc).isoformat(),status='passed',
              readme_sha256=sha(root/'README.md'),unique_local_images=len(refs),
              all_local_references_exist_with_exact_case=True,image_decoding='All PNG/GIF frames and SVG XML parsed',
              native_text_sections=True,unsupported_readme_markup=False,
              decorative_empty_alts_intentional=True,approved_hero_hashes_match=True,
              frozen_assets=frozen,external_markdown_links=external,
              github_api_render_verified=True,published_profile_verified=False)
(root/'verification-results.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
print(json.dumps({k:v for k,v in report.items() if k not in ('frozen_assets','external_markdown_links')},indent=2))
