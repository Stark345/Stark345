import os, math, random
from PIL import Image, ImageDraw, ImageFilter

def build_jarvis_morph_gif():
    w, h = 320, 360
    src_profile = r"C:\Users\ASUS\Downloads\github_profile.jpg"
    out_gif = r"E:\Stark345\assets\jarvis-neural-morph.gif"

    # 1. Base Portrait Image (Resized & Cropped)
    orig = Image.open(src_profile).convert("RGBA")
    sw, sh = orig.size
    scale = max(260 / sw, 300 / sh)
    nw, nh = int(sw * scale), int(sh * scale)
    orig_resized = orig.resize((nw, nh), Image.Resampling.LANCZOS)
    left = (nw - 260) // 2
    top = (nh - 300) // 2
    cropped_face = orig_resized.crop((left, top, left + 260, top + 300))

    # Create a dot-matrix / stippled stylized version of the portrait
    face_dots = []
    # Sample brightness and colors
    step = 5
    for y in range(0, 300, step):
        for x in range(0, 260, step):
            r, g, b, a = cropped_face.getpixel((x, y))
            brightness = (r * 0.299 + g * 0.587 + b * 0.114)
            if brightness > 25:
                rad = 1.0 + (brightness / 255.0) * 1.8
                face_dots.append((30 + x, 30 + y, (r, g, b, 255), rad))

    # 2. Draw Iron Man Mask Stage
    im_mask_img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    im_draw = ImageDraw.Draw(im_mask_img)
    cx, cy = w // 2, h // 2
    # Red Outer Helmet
    im_draw.polygon([
        (cx - 75, cy - 85), (cx + 75, cy - 85),
        (cx + 85, cy - 30), (cx + 78, cy + 50),
        (cx + 45, cy + 95), (cx - 45, cy + 95),
        (cx - 78, cy + 50), (cx - 85, cy - 30)
    ], fill="#991B1B", outline="#DC2626")
    # Gold Faceplate
    im_draw.polygon([
        (cx - 50, cy - 60), (cx + 50, cy - 60),
        (cx + 62, cy - 10), (cx + 50, cy + 45),
        (cx + 32, cy + 85), (cx - 32, cy + 85),
        (cx - 50, cy + 45), (cx - 62, cy - 10)
    ], fill="#FBBF24", outline="#F59E0B")
    # Forehead Accent
    im_draw.polygon([(cx - 28, cy - 60), (cx + 28, cy - 60), (cx + 18, cy - 35), (cx - 18, cy - 35)], fill="#B45309")
    # Cheek Indents
    im_draw.polygon([(cx - 48, cy + 10), (cx - 28, cy + 20), (cx - 28, cy + 45), (cx - 45, cy + 40)], fill="#D97706")
    im_draw.polygon([(cx + 48, cy + 10), (cx + 28, cy + 20), (cx + 28, cy + 45), (cx + 45, cy + 40)], fill="#D97706")
    # Glowing Cyan Eye Slits
    im_draw.polygon([(cx - 44, cy - 10), (cx - 16, cy - 8), (cx - 18, cy - 2), (cx - 42, cy - 4)], fill="#00F0FF")
    im_draw.polygon([(cx + 44, cy - 10), (cx + 16, cy - 8), (cx + 18, cy - 2), (cx + 42, cy - 4)], fill="#00F0FF")

    ironman_dots = []
    for y in range(40, h - 40, step):
        for x in range(40, w - 40, step):
            r, g, b, a = im_mask_img.getpixel((x, y))
            if a > 50:
                ironman_dots.append((x, y, (r, g, b, 255), 2.2))

    # 3. Draw Tech Logos Stage (React, Python, Java)
    tech_img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    t_draw = ImageDraw.Draw(tech_img)
    # React Atom (Center)
    t_draw.ellipse([cx - 14, cy - 14, cx + 14, cy + 14], fill="#00D8FF")
    for ang in [0, 60, 120]:
        rad = math.radians(ang)
        # 3 orbital ellipses
        for t in range(0, 360, 6):
            trad = math.radians(t)
            ex = 54 * math.cos(trad)
            ey = 20 * math.sin(trad)
            rx = cx + ex * math.cos(rad) - ey * math.sin(rad)
            ry = cy + ex * math.sin(rad) + ey * math.cos(rad)
            t_draw.ellipse([rx - 2, ry - 2, rx + 2, ry + 2], fill="#00D8FF")
    
    # Python Logo (Top Right corner)
    px, py = cx + 70, cy - 65
    t_draw.rounded_rectangle([px - 22, py - 22, px + 10, py + 8], radius=8, fill="#387EB8")
    t_draw.rounded_rectangle([px - 10, py - 8, px + 22, py + 22], radius=8, fill="#FFE873")
    t_draw.ellipse([px - 14, py - 14, px - 8, py - 8], fill="#FFFFFF")
    t_draw.ellipse([px + 8, py + 8, px + 14, py + 14], fill="#387EB8")

    # Java Coffee Cup (Top Left corner)
    jx, jy = cx - 70, cy - 65
    t_draw.polygon([(jx - 16, jy - 5), (jx + 16, jy - 5), (jx + 12, jy + 20), (jx - 12, jy + 20)], fill="#F89820")
    t_draw.ellipse([jx + 10, jy, jx + 22, jy + 14], outline="#5382A1", width=3)
    # Steam
    t_draw.line([(jx - 6, jy - 10), (jx - 3, jy - 22)], fill="#E76F00", width=2)
    t_draw.line([(jx + 2, jy - 8), (jx + 5, jy - 20)], fill="#E76F00", width=2)

    tech_dots = []
    for y in range(40, h - 40, step):
        for x in range(40, w - 40, step):
            r, g, b, a = tech_img.getpixel((x, y))
            if a > 40:
                tech_dots.append((x, y, (r, g, b, 255), 2.2))

    # 4. Draw JARVIS Arc Reactor / Hologram HUD Stage
    jarvis_img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    j_draw = ImageDraw.Draw(jarvis_img)
    # Outer Tech Ring
    j_draw.ellipse([cx - 85, cy - 85, cx + 85, cy + 85], outline="#00F0FF", width=2)
    # Degree Ticks
    for deg in range(0, 360, 15):
        drad = math.radians(deg)
        r1 = 88 if deg % 45 == 0 else 84
        r2 = 78
        x1 = cx + math.cos(drad) * r1
        y1 = cy + math.sin(drad) * r1
        x2 = cx + math.cos(drad) * r2
        y2 = cy + math.sin(drad) * r2
        j_draw.line([(x1, y1), (x2, y2)], fill="#38BDF8", width=1)
    
    # Inner segmented arc reactor ring
    j_draw.ellipse([cx - 62, cy - 62, cx + 62, cy + 62], outline="#0284C7", width=3)
    j_draw.ellipse([cx - 44, cy - 44, cx + 44, cy + 44], outline="#00F0FF", width=2)
    # Central Glowing Core Triangle / Hexagon
    pts = []
    for i in range(3):
        ang = math.radians(i * 120 - 90)
        pts.append((cx + math.cos(ang) * 32, cy + math.sin(ang) * 32))
    j_draw.polygon(pts, fill="#0284C7", outline="#00F0FF")
    j_draw.ellipse([cx - 16, cy - 16, cx + 16, cy + 16], fill="#FFFFFF", outline="#00F0FF")

    jarvis_dots = []
    for y in range(40, h - 40, step):
        for x in range(40, w - 40, step):
            r, g, b, a = jarvis_img.getpixel((x, y))
            if a > 40:
                jarvis_dots.append((x, y, (r, g, b, 255), 2.2))

    total_frames = 56
    frames = []

    # Stages:
    # 0..9: Face
    # 10..14: Face -> Iron Man
    # 15..23: Iron Man
    # 24..28: Iron Man -> Tech Logos
    # 29..37: Tech Logos
    # 38..42: Tech Logos -> JARVIS HUD
    # 43..51: JARVIS HUD
    # 52..55: JARVIS HUD -> Face

    random.seed(99)
    # Generate scatter positions
    scatter_dirs = [(random.uniform(-90, 90), random.uniform(-90, 90)) for _ in range(3000)]

    for f_idx in range(total_frames):
        frame = Image.new("RGBA", (w, h), "#060A14")
        f_draw = ImageDraw.Draw(frame)

        # 1. Subtle JARVIS Grid
        for gx in range(0, w, 28):
            f_draw.line([(gx, 0), (gx, h)], fill="#0B132B", width=1)
        for gy in range(0, h, 28):
            f_draw.line([(0, gy), (w, gy)], fill="#0B132B", width=1)

        # Ambient Glow in Center
        f_draw.ellipse([cx - 90, cy - 90, cx + 90, cy + 90], fill="#03254C")

        # Determine Active State & Morph Factor
        active_dots = []
        target_dots = []
        interp = 0.0

        if f_idx <= 9:
            # Face stage
            active_dots = face_dots
            interp = 0.0
        elif 10 <= f_idx <= 14:
            # Face -> Iron Man
            interp = (f_idx - 9) / 5.0
            active_dots = face_dots
            target_dots = ironman_dots
        elif 15 <= f_idx <= 23:
            # Iron Man
            active_dots = ironman_dots
            interp = 0.0
        elif 24 <= f_idx <= 28:
            # Iron Man -> Tech
            interp = (f_idx - 23) / 5.0
            active_dots = ironman_dots
            target_dots = tech_dots
        elif 29 <= f_idx <= 37:
            # Tech
            active_dots = tech_dots
            interp = 0.0
        elif 38 <= f_idx <= 42:
            # Tech -> JARVIS HUD
            interp = (f_idx - 37) / 5.0
            active_dots = tech_dots
            target_dots = jarvis_dots
        elif 43 <= f_idx <= 51:
            # JARVIS HUD
            active_dots = jarvis_dots
            interp = 0.0
        else:
            # JARVIS HUD -> Face
            interp = (f_idx - 51) / 5.0
            active_dots = jarvis_dots
            target_dots = face_dots

        # Draw Stippled Dots
        if interp == 0.0:
            for dot in active_dots:
                dx, dy, col, rad = dot
                f_draw.ellipse([dx - rad, dy - rad, dx + rad, dy + rad], fill=col)
        else:
            # Disperse and morph transition
            t = interp
            # Sine easing
            ease_t = 0.5 - 0.5 * math.cos(t * math.pi)
            
            # Draw scattering particles
            max_len = max(len(active_dots), len(target_dots))
            for i in range(max_len):
                d_src = active_dots[i % len(active_dots)]
                d_tgt = target_dots[i % len(target_dots)] if target_dots else d_src
                
                # Scatter offset
                sc_x, sc_y = scatter_dirs[i % len(scatter_dirs)]
                scatter_mult = math.sin(ease_t * math.pi) * 1.2
                
                cur_x = d_src[0] + (d_tgt[0] - d_src[0]) * ease_t + sc_x * scatter_mult
                cur_y = d_src[1] + (d_tgt[1] - d_src[1]) * ease_t + sc_y * scatter_mult
                
                # Blend color
                c1, c2 = d_src[2], d_tgt[2]
                r = int(c1[0] + (c2[0] - c1[0]) * ease_t)
                g = int(c1[1] + (c2[1] - c1[1]) * ease_t)
                b = int(c1[2] + (c2[2] - c1[2]) * ease_t)
                
                rad = d_src[3] + (d_tgt[3] - d_src[3]) * ease_t
                f_draw.ellipse([cur_x - rad, cur_y - rad, cur_x + rad, cur_y + rad], fill=(r, g, b, 255))

        # 3. JARVIS Hologram Frame Overlays
        # Corner brackets
        hud_c = "#00F0FF"
        b_len = 16
        pad = 8
        f_draw.line([(pad, pad), (pad + b_len, pad)], fill=hud_c, width=2)
        f_draw.line([(pad, pad), (pad, pad + b_len)], fill=hud_c, width=2)
        f_draw.line([(w - pad, pad), (w - pad - b_len, pad)], fill=hud_c, width=2)
        f_draw.line([(w - pad, pad), (w - pad, pad + b_len)], fill=hud_c, width=2)
        f_draw.line([(pad, h - pad), (pad + b_len, h - pad)], fill=hud_c, width=2)
        f_draw.line([(pad, h - pad), (pad, h - pad - b_len)], fill=hud_c, width=2)
        f_draw.line([(w - pad, h - pad), (w - pad - b_len, h - pad)], fill=hud_c, width=2)
        f_draw.line([(w - pad, h - pad), (w - pad, h - pad - b_len)], fill=hud_c, width=2)

        # Scanning Line
        scan_y = int((f_idx / total_frames) * h)
        f_draw.line([(pad + 2, scan_y), (w - pad - 2, scan_y)], fill="#00F0FF", width=1)

        # Top Tag
        tag_text = "VISUAL.MAP // "
        if f_idx <= 12: tag_text += "SUBJECT: S. JAICHANDRAN"
        elif 13 <= f_idx <= 26: tag_text += "AVATAR: IRON MAN MK-85"
        elif 27 <= f_idx <= 40: tag_text += "CORE: REACT • PY • JAVA"
        else: tag_text += "SYS: JARVIS ARC REACTOR"
        
        f_draw.rectangle([w // 2 - 82, pad - 2, w // 2 + 82, pad + 14], fill="#030712", outline="#0284C7")
        f_draw.text((w // 2 - 76, pad), tag_text, fill="#38BDF8", font=None)

        # Bottom Coordinate Ticker
        coord_txt = f"LAT: 13.0827°N // LNG: 80.2707°E [CYBER_HUD_v4.8]"
        f_draw.text((pad + 4, h - pad - 12), coord_txt, fill="#0284C7", font=None)

        frames.append(frame.convert("P", palette=Image.Palette.ADAPTIVE))

    frames[0].save(
        out_gif,
        save_all=True,
        append_images=frames[1:],
        duration=100,
        loop=0,
        optimize=True
    )
    print(f"Generated JARVIS Morph GIF: {out_gif} ({os.path.getsize(out_gif)} bytes)")

if __name__ == "__main__":
    build_jarvis_morph_gif()
