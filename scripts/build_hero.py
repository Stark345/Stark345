"""Build only the GitHub hero; never modifies lower README sections or raw assets.

python scripts/build_hero.py --source E:/Stark345 --output . --mask MASK.png
Later rebuilds use the committed hero-source/portrait-alpha.png, not a generated person.
Requires Pillow and numpy. No network or Git commands.
"""
from pathlib import Path
import argparse
import base64
import hashlib
import io
import json
import os
import shutil
from html import escape
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageOps

W, H, LEFT = 1440, 560, 480
SAFE = (.74, .68)
STAGES = [('Jaichandran', '01_jaichandran.png', 3000),
          ('React', '04_react.png', 2000), ('Node.js', '05_nodejs.png', 2000),
          ('MySQL', '09_mysql.png', 2000), ('Java', '06_java.png', 2000),
          ('Python', '07_python.png', 2000)]
FRAMES, FRAME_MS = 12, 50
CYAN, AQUA, WHITE, MUTED = '#6af9f1', '#54edba', '#f2fafb', '#b3d1d7'
# Hand-tuned against the approved wordmarks, not equal bounding-box dimensions.
# React's bright open symbol and Python's dense fill need less area; wide MySQL
# and Java stay at the approved maximum width. Portrait placement is untouched.
OPTICAL_FACTORS = {'React': .81, 'Node.js': .96, 'MySQL': 1, 'Java': 1, 'Python': .72}


def font(size, bold=False):
    for root in [Path(os.environ.get('WINDIR', 'C:/Windows'))/'Fonts', Path('/usr/share/fonts/truetype/dejavu')]:
        for name in (['segoeuib.ttf', 'DejaVuSans-Bold.ttf'] if bold else ['segoeui.ttf', 'DejaVuSans.ttf']):
            if (root/name).exists():
                return ImageFont.truetype(str(root/name), size)
    raise RuntimeError('Segoe UI or DejaVu Sans required.')


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def background(banner, width=W, height=H, mobile=False):
    # Atmospheric geometry echoes the source banner, never a reactor widget.
    yy, xx = np.mgrid[:height, :width]
    x, y = xx/width, yy/height
    rgb = np.zeros((height, width, 3), dtype=np.float32) + [2, 9, 17]
    glows = [(.12, .50, .30, .62, [0, 32, 35]),
             (.02, .82, .22, .24, [0, 66, 40]),
             (.72, .0, .46, .66, [0, 15, 34]),
             (.92, .85, .34, .28, [0, 26, 32])]
    for cx, cy, sx, sy, col in glows:
        g = np.exp(-((x-cx)/sx)**2-((y-cy)/sy)**2)
        rgb += g[:, :, None]*col
    # Broad off-canvas planetary limb; no enclosed rings or technical ticks.
    radius = np.sqrt(((x+.19)/.43)**2+((y-.06)/.92)**2)
    rim = np.exp(-((radius-1)/.009)**2)*.75 + np.exp(-((radius-1)/.05)**2)*.22
    rgb += rim[:, :, None]*[0, 56, 37]
    # Low-frequency mist, not a cloud of decorative particles.
    fog = (np.sin(x*13+y*18)+np.sin(x*31-y*9)+np.cos(x*57+y*7))/3
    fog *= np.exp(-((y-.79)/.22)**2)
    rgb += fog[:, :, None]*[0, 6, 7]
    im = Image.fromarray(np.clip(rgb, 0, 255).astype('uint8')).convert('RGBA')
    # Reuse only the text-free mountain foreground of the actual primary reference.
    land = banner.crop((0, 624, banner.width, banner.height))
    lh = round(height*(.24 if mobile else .34))
    land = land.resize((width, lh), Image.Resampling.LANCZOS).convert('RGBA')
    fade = (np.linspace(0, 1, lh)**1.3*235).astype('uint8')
    land.putalpha(Image.fromarray(np.tile(fade[:, None], (1, width))))
    im.alpha_composite(land, (0, height-lh))
    # Restrained lighting streak, behind the copy and never a UI border.
    light = Image.new('RGBA', im.size)
    d = ImageDraw.Draw(light)
    if not mobile:
        d.line((485, 280, 830, 280, 1400, 273), fill=(67, 238, 219, 70), width=2)
        d.ellipse((760, 275, 788, 283), fill=(85, 255, 224, 110))
    im.alpha_composite(light.filter(ImageFilter.GaussianBlur(7)))
    return im


def clean_logo(path, name):
    im = Image.open(path).convert('RGBA')
    a = np.array(im)
    rgb = a[:, :, :3].astype(float)
    hi, lo = rgb.max(2), rgb.min(2)
    sat = hi-lo
    local_sat = np.asarray(Image.fromarray(sat.astype('uint8')).filter(ImageFilter.MaxFilter(5))).astype(float)
    coverage = np.clip(sat/np.maximum(local_sat, 1), 0, 1)
    alpha = np.clip((sat-8)/20, 0, 1)*coverage
    # Unmatte antialiased edge pixels against the baked white/gray checkerboard.
    # Without this, a bright white outline remains on a dark hero.
    foreground = (rgb-(1-coverage[:, :, None])*245)/np.maximum(coverage[:, :, None], .01)
    a[:, :, :3] = np.clip(foreground, 0, 255).astype('uint8')
    if name == 'MySQL':
        blue = (rgb[:, :, 2] > rgb[:, :, 0]+25) & (sat > 15)
        a[blue, :3] = np.clip(a[blue, :3].astype(float)*1.32, 0, 255).astype('uint8')
    if name == 'Node.js':
        alpha = np.maximum(alpha, np.clip((155-hi)/45, 0, 1))
        # Source gray wordmark becomes silver for contrast; green JS is unchanged.
        neutral = (sat < 22) & (hi < 155)
        a[neutral, :3] = [218, 237, 239]
    a[:, :, 3] = np.minimum(a[:, :, 3], np.round(alpha*255).astype('uint8'))
    clean = Image.fromarray(a)
    return clean.crop(clean.getchannel('A').getbbox())


def portrait_from_original(original, mask, dest):
    rgb = Image.open(original).convert('RGB')
    cut = Image.open(mask)
    alpha = cut.getchannel('A') if cut.mode == 'RGBA' else cut.convert('L')
    if alpha.size != rgb.size:
        raise ValueError('Mask must align exactly with the original; no subject warping allowed.')
    # The extraction mask's nominally opaque interior was 252–254, not 255.
    # Restore full opacity there; retain soft hair/edge values below that level.
    alpha = alpha.point(lambda v: 255 if v >= 250 else v)
    out = rgb.convert('RGBA')
    out.putalpha(alpha)
    out.save(dest/'jaichandran-cutout.png')
    alpha.save(dest/'portrait-alpha.png')
    # No generated RGB pixels enter the final cutout, including transparent areas.
    assert np.array_equal(np.asarray(out)[:, :, :3], np.asarray(rgb))
    assert alpha.getextrema() == (0, 255)
    return out


def layer_for(name, asset):
    layer = Image.new('RGBA', (LEFT, H))
    if name == 'Jaichandran':
        fit = ImageOps.contain(asset, (422, 500), Image.Resampling.LANCZOS)
        xy = ((LEFT-fit.width)//2, 43)
        a = np.asarray(fit.getchannel('A')).astype(float)
        # Bottom fade is presentation only; high-resolution cutout stays intact.
        fade = np.clip((fit.height-1-np.arange(fit.height))/58, 0, 1)
        side = np.minimum(np.clip(np.arange(fit.width)/16, 0, 1), np.clip((fit.width-1-np.arange(fit.width))/20, 0, 1))
        fit.putalpha(Image.fromarray((a*fade[:, None]*side[None, :]).astype('uint8')))
    else:
        # Wide wordmarks get full safe width; compact symbols deliberately smaller.
        fac = OPTICAL_FACTORS[name]
        fit = ImageOps.contain(asset, (round(LEFT*SAFE[0]*fac), round(H*SAFE[1]*fac)), Image.Resampling.LANCZOS)
        # Centroid correction balances visible ink while retaining the entire mark.
        weights = np.asarray(fit.getchannel('A')).astype(float)/255
        ys, xs = np.mgrid[:fit.height, :fit.width]
        cx, cy = (weights*xs).sum()/weights.sum(), (weights*ys).sum()/weights.sum()
        dx = np.clip(fit.width/2-cx, -12, 12)
        dy = np.clip(fit.height/2-cy, -15, 15)
        xy = (round((LEFT-fit.width)/2+dx), round((H-fit.height)/2+dy))
    layer.alpha_composite(fit, xy)
    return layer, fit.size, xy


def lit(layer, portrait=False):
    a = layer.getchannel('A')
    out = Image.new('RGBA', layer.size)
    if portrait:
        # Glow sits outside the cutout; no grading or repainting of the face.
        outer = a.filter(ImageFilter.MaxFilter(7)).filter(ImageFilter.GaussianBlur(14))
        rim = Image.new('RGBA', layer.size, (41, 229, 187, 0))
        rim.putalpha(outer.point(lambda v: round(v*.32)))
        out.alpha_composite(rim)
    else:
        glow = Image.new('RGBA', layer.size, (62, 221, 230, 0))
        glow.putalpha(a.filter(ImageFilter.GaussianBlur(8)).point(lambda v: round(v*.15)))
        out.alpha_composite(glow)
    out.alpha_composite(layer)
    return out


def ribbon(base, icon_root, box, mobile=False):
    x, y, width, height = box
    panel = Image.new('RGBA', base.size)
    d = ImageDraw.Draw(panel)
    d.rounded_rectangle((x, y, x+width, y+height), radius=17, fill=(7, 28, 40, 160))
    d.line((x+20, y, x+width-20, y), fill=(94, 220, 225, 90), width=1)
    d.line((x+20, y+height, x+width-20, y+height), fill=(70, 163, 181, 45), width=1)
    base.alpha_composite(panel)
    names = [('Python','python'),('Java','java'),('React','react'),('Node.js','nodejs'),
             ('Express','express'),('MongoDB','mongodb'),('MySQL','mysql'),
             ('TensorFlow','tensorflow'),('OpenCV','opencv'),('LLMs',None),('RAG',None),('Vector DB',None)]
    cols, gap, size = (4, 55, 20) if mobile else (6, 54, 18)
    cell = width/cols
    d = ImageDraw.Draw(base)
    for i, (label, icon) in enumerate(names):
        px, py = round(x+18+(i%cols)*cell), y+17+(i//cols)*gap
        if icon:
            mark = Image.open(icon_root/f'{icon}.png').convert('RGBA')
            if icon == 'express':
                a = np.array(mark); a[:, :, :3] = [222, 242, 244]; mark = Image.fromarray(a)
            mark = ImageOps.contain(mark, (28, 30), Image.Resampling.LANCZOS)
            base.alpha_composite(mark, (px, py+(30-mark.height)//2))
            px += 35
        d.text((px, py+2), label, font=font(size), fill=WHITE if i < 6 else MUTED)


def layout(banner, icons, mobile=False):
    im = background(banner, 720 if mobile else W, 1000 if mobile else H, mobile)
    d = ImageDraw.Draw(im)
    if mobile:
        d.text((40, 37), 'S. Jaichandran', font=font(66, True), fill=CYAN)
        d.text((42, 121), 'AI-Integrated Full-Stack Developer', font=font(31), fill=WHITE)
        ribbon(im, icons, (30, 769, 660, 180), True)
        d.text((42, 964), 'Building intelligent full-stack systems powered by AI.', font=font(22), fill=MUTED)
    else:
        d.text((502, 84), 'BUILDING INTELLIGENT SOLUTIONS', font=font(17), fill=AQUA)
        d.text((497, 120), 'S. ', font=font(80, True), fill=WHITE)
        tx = 497+d.textlength('S. ', font=font(80, True))
        d.text((tx, 120), 'Jaichandran', font=font(80, True), fill=CYAN)
        d.text((503, 223), 'AI-Integrated Full-Stack Developer', font=font(34), fill=WHITE)
        ribbon(im, icons, (494, 317, 898, 115))
        d.text((503, 468), 'Building intelligent full-stack systems powered by AI.', font=font(23), fill='#c1e1df')
    return im


def scan_transition(source, target, step):
    p = (step+1)/(FRAMES+1)
    aa = np.maximum(np.asarray(source.getchannel('A')), np.asarray(target.getchannel('A')))
    occupied = np.where(aa > 8)[0]
    # Scan the occupied image height, so blank margins do not extend formed holds.
    start, end = int(occupied.min())-3, int(occupied.max())+3
    scan = start+(end-start)*p
    yy = np.arange(H)[:, None]
    mask = np.broadcast_to(np.clip((scan-yy+2)/4, 0, 1)*255, (H, LEFT)).astype('uint8').copy()
    out = Image.composite(target, source, Image.fromarray(mask))
    # Sample only real silhouette edges crossing the scan, deterministically.
    silhouette = Image.fromarray(aa)
    edge = np.asarray(silhouette.filter(ImageFilter.FIND_EDGES)) > 22
    band = np.abs(np.arange(H)[:, None]-scan) < 12
    ys, xs = np.where(edge & band & (aa > 18))
    d = ImageDraw.Draw(out)
    if len(xs):
        stride = max(1, len(xs)//44)
        for k in range(0, len(xs), stride):
            sx, sy = int(xs[k]), int(ys[k])
            # Tiny motion is derived from each source edge, never a random cloud.
            dx = round(3*np.sin(sx*.39+sy*.23+step*.5))
            dy = round(4*np.cos(sx*.19+step*.7))
            d.line((sx, sy, sx+dx, sy+dy), fill=(110, 247, 226, 185), width=1)
        line_y = round(scan)
        if 0 <= line_y < H:
            for px in np.flatnonzero(aa[line_y] > 24):
                d.point((int(px), line_y), fill=(124, 254, 239, 235))
    return out


def compose(base, stage, mobile=False):
    out = base.copy()
    out.alpha_composite(stage, (120, 183) if mobile else (0, 0))
    return out.convert('RGB')


def encode_gif(frames, durations, path, static_boxes=(), portrait_offset=(0, 0)):
    # One shared palette prevents stationary type/ribbon shimmer.
    sheet = Image.new('RGB', (frames[0].width, frames[0].height*6))
    for i in range(6):
        sheet.paste(frames[i*(FRAMES+1)], (0, i*frames[0].height))
    # Reserve fresh original-photo skin tones; a scene-only palette starves the
    # single portrait stage and causes severe orange/blue dithering on the face.
    ox, oy = portrait_offset
    face = frames[0].crop((155+ox,100+oy,350+ox,430+oy)).quantize(colors=112, method=Image.Quantize.MEDIANCUT)
    scene = sheet.quantize(colors=128, method=Image.Quantize.MEDIANCUT)
    exact = [(106,249,241),(84,237,186),(242,250,251),(179,209,215),
             (193,225,223),(0,0,0),(255,255,255),(62,221,230),
             (251,24,32),(0,139,184),(0,146,192),(255,142,0),
             (116,178,79),(55,121,169),(255,210,47),(97,218,251)]
    palette = Image.new('P', (1,1))
    palette_lock = path.parent/'hero-source/gif-palettes.json'
    locked = json.loads(palette_lock.read_text()) if palette_lock.exists() else {}
    # Resizing a logo must not re-quantize the approved portrait/background/type.
    palette.putpalette(locked.get(path.name, face.getpalette()[:112*3]+scene.getpalette()[:128*3]+[v for c in exact for v in c]))
    indexed = [f.quantize(palette=palette, dither=Image.Dither.FLOYDSTEINBERG) for f in frames]
    for static_box in static_boxes:
        patch = indexed[0].crop(static_box)
        for q in indexed:
            q.paste(patch, static_box[:2])
    indexed[0].save(path, save_all=True, append_images=indexed[1:], duration=durations,
                    loop=0, optimize=True, disposal=1)
    with Image.open(path) as gif:
        actual = []
        for i in range(gif.n_frames):
            gif.seek(i); actual.append(gif.info['duration'])
        assert actual == durations, (path.name, actual, durations)
        assert sum(actual) == 16600 and gif.info['loop'] == 0


def preview_html():
    cards = ''.join(f'<figure><img src="assets/hero-review/{i:02d}-{name.lower().replace(".", "")}.png" alt="{name} formed state"><figcaption>{name} — {ms/1000:g} seconds</figcaption></figure>' for i,(name,_,ms) in enumerate(STAGES))
    return '''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Jaichandran · Hero review</title><style>
*{box-sizing:border-box}body{margin:0;background:#030a12;color:#e8fafa;font:16px/1.6 system-ui}main{max-width:1488px;margin:auto;padding:24px}h1{font-size:22px}h2{font-size:18px;margin-top:32px}p,figcaption{color:#b3d1d7}img{display:block;width:100%;height:auto}.mobile{max-width:390px}.gallery{display:grid;grid-template-columns:repeat(2,1fr);gap:16px}figure{margin:0}button{padding:10px 20px;background:#0c2630;color:#a5ffdf;border:1px solid #38656c;border-radius:6px}a{color:#72efdd}@media(max-width:600px){main{padding:16px}.gallery{grid-template-columns:1fr}}
</style></head><body><main><h1>S. Jaichandran · Hero review</h1><p>Hero only. No lower-section changes. Not committed or pushed.</p><button id="pause">Pause animation</button><h2>Desktop · complete loop</h2><img data-motion="assets/hero-cinematic.gif" data-still="assets/hero-cinematic.png" src="assets/hero-cinematic.gif" width="1440" height="560" alt="Jaichandran, React, Node.js, MySQL, Java, Python"><p>Jaichandran 3s · technology stages 2s · scan transitions 0.6s · full loop 16.6s</p><h2>Mobile · 390px display width</h2><img class="mobile" data-motion="assets/hero-mobile.gif" data-still="assets/hero-mobile.png" src="assets/hero-mobile.gif" width="720" height="1000" alt="Mobile hero layout"><h2>All six formed states</h2><div class="gallery">'''+cards+'''</div><h2>Primary reference</h2><img src="assets/morph_stages/banner_theme.png" alt="Supplied banner theme"><script>
let paused=matchMedia('(prefers-reduced-motion: reduce)').matches;const b=document.getElementById('pause');function sync(){document.querySelectorAll('[data-motion]').forEach(i=>i.src=paused?i.dataset.still:i.dataset.motion);b.textContent=paused?'Play animation':'Pause animation';b.setAttribute('aria-pressed',String(paused))}b.onclick=()=>{paused=!paused;sync()};sync();</script></main></body></html>'''


def build(source, output, mask):
    raw, assets = source/'assets/morph_stages', output/'assets'
    review, originals = assets/'hero-review', assets/'hero-source'
    for p in [review, originals, assets/'morph_stages']:
        p.mkdir(parents=True, exist_ok=True)
    mask = mask or source/'assets/hero-source/portrait-alpha.png'
    portrait = portrait_from_original(raw/'01_jaichandran.png', mask, originals)
    banner = Image.open(raw/'banner_theme.png').convert('RGB')
    icons = source/'scripts/evidence/icons'
    layers, records = [], []
    for name, filename, hold in STAGES:
        asset = portrait if name == 'Jaichandran' else clean_logo(raw/filename, name)
        if name != 'Jaichandran':
            asset.save(originals/f'{name.lower().replace(".", "")}-clean.png')
        layer, size, xy = layer_for(name, asset)
        if name != 'Jaichandran':
            assert size[0] <= round(LEFT*SAFE[0]) and size[1] <= round(H*SAFE[1])
            assert xy[0] >= 0 and xy[1] >= 0 and xy[0]+size[0] <= LEFT and xy[1]+size[1] <= H
            assert abs(size[0]/size[1]-asset.width/asset.height) < .015
        layers.append(lit(layer, name == 'Jaichandran'))
        records.append(dict(name=name, source=filename, source_sha256=sha(raw/filename), hold_ms=hold,
                            displayed_size=size, position=xy, cleaned_source_size=list(asset.size)))
    desktop, mobile = layout(banner, icons), layout(banner, icons, True)
    frames, mobile_frames, morph_frames, durations = [], [], [], []
    for i, layer in enumerate(layers):
        formed = compose(desktop, layer)
        formed.save(review/f'{i:02d}-{STAGES[i][0].lower().replace(".", "")}.png')
        cycle = [(layer, STAGES[i][2])]+[(scan_transition(layer, layers[(i+1)%6], step), FRAME_MS) for step in range(FRAMES)]
        for moving, duration in cycle:
            frames.append(compose(desktop, moving))
            mobile_frames.append(compose(mobile, moving, True))
            morph_frames.append(frames[-1].crop((0, 0, LEFT, H)))
            durations.append(duration)
    frames[0].save(assets/'hero-cinematic.png')
    mobile_frames[0].save(assets/'hero-mobile.png')
    frames[0].resize((1012, round(H*1012/W)), Image.Resampling.LANCZOS).save(review/'desktop-1012.png')
    mobile_frames[0].resize((390, round(1000*390/720)), Image.Resampling.LANCZOS).save(review/'mobile-390.png')
    print('Static previews ready.', flush=True)
    encode_gif(frames, durations, assets/'hero-cinematic.gif', ((LEFT, 0, W, H),))
    print('Desktop loop ready.', flush=True)
    encode_gif(mobile_frames, durations, assets/'hero-mobile.gif',
               ((0,0,720,183), (0,743,720,1000), (0,183,120,743), (600,183,720,743)), (120,183))
    encode_gif(morph_frames, durations, assets/'jarvis-morph.gif')
    right = desktop.crop((LEFT, 0, W, H)).convert('RGB')
    right.save(assets/'hero-right.png')
    buf = io.BytesIO(); right.save(buf, format='PNG')
    (assets/'jarvis-hero-console.svg').write_text(f'<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" viewBox="0 0 {right.width} {right.height}"><title>S. Jaichandran — AI-Integrated Full-Stack Developer</title><image width="{right.width}" height="{right.height}" xlink:href="data:image/png;base64,{base64.b64encode(buf.getvalue()).decode()}"/></svg>\n', encoding='utf-8')
    contact = Image.new('RGB', (1440, 3*305), '#030a12')
    d = ImageDraw.Draw(contact)
    with Image.open(assets/'hero-cinematic.gif') as gif:
        for i in range(6):
            gif.seek(i*(FRAMES+1))
            tile = gif.convert('RGB').resize((720, 280), Image.Resampling.LANCZOS)
            pos = ((i%2)*720, (i//2)*305)
            contact.paste(tile, pos)
            d.text((pos[0]+10, pos[1]+280), STAGES[i][0], font=font(16), fill=MUTED)
        gif.seek(6); gif.convert('RGB').save(review/'scan-transition.png')
        gif.seek(0); gif.convert('RGB').save(review/'gif-portrait-decoded.png')
    contact.save(assets/'hero-contact-sheet.png')
    manifest = dict(canvas=[W,H], mobile_canvas=[720,1000], morph_area=[LEFT,H], logo_safe_area=list(SAFE),
                    optical_scale_factors=OPTICAL_FACTORS,
                    transition_ms=FRAMES*FRAME_MS, loop_ms=sum(durations), frame_count=len(frames), stages=records,
                    portrait_source='assets/morph_stages/01_jaichandran.png',
                    portrait_original_rgb_exact=True, portrait_alpha_sha256=sha(originals/'portrait-alpha.png'),
                    banner_sha256=sha(raw/'banner_theme.png'), particle_source='silhouette edges crossing scan front',
                    excluded_hero_assets=['02_ironman.jpg','03_arc_reactor.png','08_cyber_ai.png'],
                    reserved_lower_section_assets=['02_ironman.jpg','03_arc_reactor.png'])
    (assets/'hero-manifest.json').write_text(json.dumps(manifest, indent=2)+'\n', encoding='utf-8')
    (output/'preview_morph.html').write_text(preview_html(), encoding='utf-8')
    if (raw/'banner_theme.png').resolve() != (assets/'morph_stages/banner_theme.png').resolve():
        shutil.copy2(raw/'banner_theme.png', assets/'morph_stages/banner_theme.png')
    # Update only the first hero alt text. Everything below its picture is untouched.
    readme = (source/'README.md').read_bytes()
    old = b'portrait, React, Node.js, Java, Python, Cyber AI.'
    new = b'portrait, React, Node.js, MySQL, Java, Python.'
    assert old in readme or new in readme
    patched = readme.replace(old, new, 1)
    assert patched.split(b'</picture>', 1)[1] == readme.split(b'</picture>', 1)[1]
    (output/'README.md').write_bytes(patched)
    print(json.dumps(dict(output=str(output), frames=len(frames), duration_ms=sum(durations),
                          gif_bytes={p.name:p.stat().st_size for p in assets.glob('*.gif')}), indent=2))


if __name__ == '__main__':
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--source', type=Path, default=Path(__file__).resolve().parents[1])
    ap.add_argument('--output', type=Path)
    ap.add_argument('--mask', type=Path)
    args = ap.parse_args()
    build(args.source.resolve(), (args.output or args.source).resolve(), args.mask)
