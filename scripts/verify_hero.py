"""Verify installed approved hero bytes, decoding, timing and original portrait pixels.

Never generates or modifies hero assets. Writes only hero-verification.json.
"""
from pathlib import Path
from datetime import datetime, timezone
import argparse
import hashlib
import json
import re
import numpy as np
from PIL import Image


def digest(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def verify(source, output):
    assets = output/'assets'
    manifest = json.loads((assets/'hero-manifest.json').read_text())
    installation = json.loads((output/'docs/hero-installation.json').read_text(encoding='utf-8-sig'))
    frozen = [record for record in installation['files'] if record['frozen']]
    for record in frozen:
        assert digest(output/record['path']) == record['staged_sha256'], record['path']
    expected_names = ['Jaichandran', 'React', 'Node.js', 'MySQL', 'Java', 'Python']
    assert [s['name'] for s in manifest['stages']] == expected_names
    assert [s['displayed_size'] for s in manifest['stages'][1:]] == [[288,257],[341,208],[355,184],[355,176],[256,246]]
    expected = []
    for name in expected_names:
        expected.extend([3000 if name == 'Jaichandran' else 2000]+[50]*12)
    loops = {}
    for filename, size in [('hero-cinematic.gif', (1440,560)), ('hero-mobile.gif', (720,1000)), ('jarvis-morph.gif', (480,560))]:
        with Image.open(assets/filename) as gif:
            assert gif.size == size
            assert gif.info['loop'] == 0
            durations = []
            first = None
            max_drift = 0
            for n in range(gif.n_frames):
                gif.seek(n)
                a = np.asarray(gif.convert('RGB')).copy()
                durations.append(gif.info['duration'])
                if first is None:
                    first = a
                if filename == 'hero-cinematic.gif':
                    max_drift = max(max_drift, int(np.abs(a[:,480:].astype(int)-first[:,480:].astype(int)).max()))
                if filename == 'hero-mobile.gif':
                    for region in [np.s_[:183,:], np.s_[743:,:], np.s_[:,:120], np.s_[:,600:]]:
                        max_drift = max(max_drift, int(np.abs(a[region].astype(int)-first[region].astype(int)).max()))
            assert durations == expected, (filename, durations)
            assert max_drift == 0, (filename, max_drift)
            loops[filename] = dict(size=list(size), frames=len(durations), duration_ms=sum(durations),
                                   static_region_max_drift=max_drift, bytes=(assets/filename).stat().st_size)
    original = np.asarray(Image.open(source/'assets/morph_stages/01_jaichandran.png').convert('RGB'))
    cutout = np.asarray(Image.open(assets/'hero-source/jaichandran-cutout.png').convert('RGBA'))
    assert original.shape == cutout[:,:,:3].shape
    assert np.array_equal(original, cutout[:,:,:3])
    assert cutout[:,:,3].min() == 0 and cutout[:,:,3].max() == 255
    assert (cutout[400:630,470:755,3] == 255).all(), 'Face core unexpectedly transparent'
    for stage in manifest['stages']:
        assert stage['source_sha256'] == digest(source/'assets/morph_stages'/stage['source'])
        if stage['name'] != 'Jaichandran':
            w,h=stage['displayed_size']; x,y=stage['position']
            assert w <= round(480*.74) and h <= round(560*.68)
            assert x >= 0 and y >= 0 and x+w <= 480 and y+h <= 560
    assert manifest['banner_sha256'] == digest(source/'assets/morph_stages/banner_theme.png')
    after = (output/'README.md').read_bytes()
    assert b'Cyber AI' not in after.split(b'</picture>',1)[0]
    assert b'MySQL' in after.split(b'</picture>',1)[0]
    html = (output/'preview_morph.html').read_text(encoding='utf-8')
    refs = set(re.findall(r'(?:src|data-motion|data-still)="([^"]+)"', html))
    assert all((output/r).is_file() for r in refs)
    source_files = ['README.md','scripts/build_hero.py','preview_morph.html',
                    'assets/hero-cinematic.gif','assets/hero-mobile.gif','assets/hero-source/approved-portrait.png',
                    'assets/morph_stages/01_jaichandran.png','assets/morph_stages/02_ironman.jpg',
                    'assets/morph_stages/03_arc_reactor.png','assets/morph_stages/08_cyber_ai.png']
    report = dict(status='passed', checked_at=datetime.now(timezone.utc).isoformat(),
                  installation='Installed from approved staging bytes; measured after lower-section changes',
                  frozen_files_checked=len(frozen), approved_hashes_match=True,
                  stages=expected_names, loops=loops, original_portrait_rgb_exact=True,
                  cutout_resolution=[cutout.shape[1],cutout.shape[0]],
                  raw_source_hashes_match=True,
                  preview_references_valid=len(refs), published_github_profile_verified=False,
                  browser_playback_report='docs/browser-verification.json',
                  source_fingerprints={name:digest(source/name) for name in source_files if (source/name).is_file()})
    (output/'hero-verification.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(report,indent=2))


if __name__ == '__main__':
    p=argparse.ArgumentParser()
    p.add_argument('--source',type=Path,required=True)
    p.add_argument('--output',type=Path,required=True)
    a=p.parse_args(); verify(a.source,a.output)
